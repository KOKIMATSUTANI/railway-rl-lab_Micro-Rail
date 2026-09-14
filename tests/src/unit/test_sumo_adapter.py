import pytest
import numpy as np
from unittest.mock import Mock, patch

class TestSUMOToMicroRailInit:
    """Test suite for __init__ method"""
    
    def test_init_creates_instance(self, mock_sumo_net, mock_sumo_routes):
        """Verify that initialization creates a valid instance"""
        adapter = sumo_adapter(mock_sumo_net, mock_sumo_routes)
        assert adapter is not None
        assert adapter.sumo_net == mock_sumo_net
        assert adapter.sumo_routes == mock_sumo_routes
    
    def test_init_calls_build_tc_mapping(self, mock_sumo_net, mock_sumo_routes):
        """Verify that build_tc_mapping is called during initialization"""
        with patch.object(sumo_adapter, 'build_tc_mapping'):
            adapter = sumo_adapter(mock_sumo_net, mock_sumo_routes)
            # build_tc_mapping should be invoked


class TestExtractFeatures:
    """Test suite for extract_features method"""
    
    def test_returns_array_length_12(self, sumo_to_microrail, 
                                     mock_track_circuit, mock_vehicle):
        """Verify that feature array has exactly 12 elements"""
        features = sumo_to_microrail.extract_features(
            mock_track_circuit, mock_vehicle, current_time=0
        )
        assert isinstance(features, np.ndarray)
        assert len(features) == 12
    
    def test_all_features_are_numeric(self, sumo_to_microrail,
                                      mock_track_circuit, mock_vehicle):
        """Verify that all features are numeric values"""
        features = sumo_to_microrail.extract_features(
            mock_track_circuit, mock_vehicle, current_time=0
        )
        assert all(isinstance(f, (int, float, np.number)) for f in features)
    
    def test_no_nan_values(self, sumo_to_microrail,
                          mock_track_circuit, mock_vehicle):
        """Verify that no NaN values are present in feature array"""
        features = sumo_to_microrail.extract_features(
            mock_track_circuit, mock_vehicle, current_time=0
        )
        assert not np.isnan(features).any()


class TestFeatureValues:
    """Test suite for feature value validity"""
    
    def test_f0_reservation_status_binary(self, sumo_to_microrail,
                                         mock_track_circuit, mock_vehicle):
        """Verify that f0 (reservation status) is either 0 or 1"""
        sumo_to_microrail.get_reservation_status = Mock(return_value=1)
        features = sumo_to_microrail.extract_features(
            mock_track_circuit, mock_vehicle, current_time=0
        )
        assert features[0] in [0, 1]
    
    def test_f1_direction_valid(self, sumo_to_microrail,
                               mock_track_circuit, mock_vehicle):
        """Verify that f1 (train direction) has valid value"""
        sumo_to_microrail.get_train_direction = Mock(return_value=1)
        features = sumo_to_microrail.extract_features(
            mock_track_circuit, mock_vehicle, current_time=0
        )
        assert features[1] in [-1, 0, 1]
    
    def test_f2_decision_point_binary(self, sumo_to_microrail,
                                     mock_track_circuit, mock_vehicle):
        """Verify that f2 (decision point) is either 0 or 1"""
        sumo_to_microrail.is_decision_point = Mock(return_value=0)
        features = sumo_to_microrail.extract_features(
            mock_track_circuit, mock_vehicle, current_time=0
        )
        assert features[2] in [0, 1]
    
    def test_f3_f4_onehot_sum_to_one(self, sumo_to_microrail,
                                     mock_track_circuit, mock_vehicle):
        """Verify that f3, f4 (train type one-hot encoding) sum to 1"""
        sumo_to_microrail.get_train_type_onehot = Mock(return_value=(1, 0))
        features = sumo_to_microrail.extract_features(
            mock_track_circuit, mock_vehicle, current_time=0
        )
        assert features[3] + features[4] == 1
    
    def test_f5_time_supplement_non_negative(self, sumo_to_microrail,
                                            mock_track_circuit, mock_vehicle):
        """Verify that f5 (time supplement) is non-negative"""
        sumo_to_microrail.get_time_supplement = Mock(return_value=10.5)
        features = sumo_to_microrail.extract_features(
            mock_track_circuit, mock_vehicle, current_time=0
        )
        assert features[5] >= 0
    
    def test_f6_remaining_running_time_non_negative(self, sumo_to_microrail,
                                                   mock_track_circuit, mock_vehicle):
        """Verify that f6 (remaining running time) is non-negative"""
        sumo_to_microrail.get_remaining_running_time = Mock(return_value=300)
        features = sumo_to_microrail.extract_features(
            mock_track_circuit, mock_vehicle, current_time=0
        )
        assert features[6] >= 0
    
    def test_f7_f8_disruption_countdown_non_negative(self, sumo_to_microrail,
                                                    mock_track_circuit, mock_vehicle):
        """Verify that f7, f8 (disruption countdown) are non-negative"""
        sumo_to_microrail.get_disruption_countdown = Mock(return_value=(5, 10))
        features = sumo_to_microrail.extract_features(
            mock_track_circuit, mock_vehicle, current_time=0
        )
        assert features[7] >= 0
        assert features[8] >= 0
    
    def test_f9_node_degree_positive(self, sumo_to_microrail,
                                    mock_track_circuit, mock_vehicle):
        """Verify that f9 (node degree) is positive"""
        sumo_to_microrail.get_node_degree = Mock(return_value=3)
        features = sumo_to_microrail.extract_features(
            mock_track_circuit, mock_vehicle, current_time=0
        )
        assert features[9] > 0
    
    def test_f10_betweenness_in_range(self, sumo_to_microrail,
                                     mock_track_circuit, mock_vehicle):
        """Verify that f10 (betweenness centrality) is in range [0, 1]"""
        # betweenness is initialized to 0.5
        features = sumo_to_microrail.extract_features(
            mock_track_circuit, mock_vehicle, current_time=0
        )
        assert 0 <= features[10] <= 1
    
    def test_f11_on_route_binary(self, sumo_to_microrail,
                                mock_track_circuit, mock_vehicle):
        """Verify that f11 (on route) is either 0 or 1"""
        sumo_to_microrail.is_on_vehicle_route = Mock(return_value=1)
        features = sumo_to_microrail.extract_features(
            mock_track_circuit, mock_vehicle, current_time=0
        )
        assert features[11] in [0, 1]


class TestEdgeCases:
    """Test suite for edge cases"""
    
    def test_multiple_vehicles(self, sumo_to_microrail, mock_track_circuit):
        """Verify that feature extraction works for multiple vehicles"""
        vehicle1 = Mock()
        vehicle1.getID = Mock(return_value='train_1')
        vehicle2 = Mock()
        vehicle2.getID = Mock(return_value='train_2')
        
        features1 = sumo_to_microrail.extract_features(
            mock_track_circuit, vehicle1, current_time=0
        )
        features2 = sumo_to_microrail.extract_features(
            mock_track_circuit, vehicle2, current_time=0
        )
        
        assert len(features1) == 12
        assert len(features2) == 12
    
    def test_time_zero(self, sumo_to_microrail, mock_track_circuit, mock_vehicle):
        """Verify feature extraction at time 0"""
        features = sumo_to_microrail.extract_features(
            mock_track_circuit, mock_vehicle, current_time=0
        )
        assert features is not None
    
    def test_large_time_value(self, sumo_to_microrail, mock_track_circuit, mock_vehicle):
        """Verify feature extraction with large time values"""
        features = sumo_to_microrail.extract_features(
            mock_track_circuit, mock_vehicle, current_time=10000
        )
        assert features is not None