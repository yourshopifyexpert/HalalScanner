/**
 * History Screen - Display scan history
 */

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Image,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Icon from 'react-native-vector-icons/MaterialIcons';
import ResultsModal from '../components/ResultsModal';

const HistoryScreen = () => {
  const [history, setHistory] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const historyData = await AsyncStorage.getItem('scanHistory');
      if (historyData) {
        const historyArray = JSON.parse(historyData);
        setHistory(historyArray);
      }
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadHistory();
    setRefreshing(false);
  };

  const handleItemPress = (item: any) => {
    setSelectedItem(item);
    setShowResults(true);
  };

  const handleCloseResults = () => {
    setShowResults(false);
    setSelectedItem(null);
  };

  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'HALAL':
        return '#27ae60';
      case 'HARAM':
        return '#e74c3c';
      case 'SUSPICIOUS':
        return '#f39c12';
      case 'UNKNOWN':
        return '#95a5a6';
      default:
        return '#95a5a6';
    }
  };

  const getVerdictIcon = (verdict: string) => {
    switch (verdict) {
      case 'HALAL':
        return 'check-circle';
      case 'HARAM':
        return 'cancel';
      case 'SUSPICIOUS':
        return 'warning';
      case 'UNKNOWN':
        return 'help';
      default:
        return 'help';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const renderItem = ({item}: {item: any}) => (
    <TouchableOpacity
      style={styles.historyItem}
      onPress={() => handleItemPress(item)}>
      <View style={styles.imageContainer}>
        {item.imageUri ? (
          <Image source={{uri: item.imageUri}} style={styles.thumbnail} />
        ) : (
          <View style={styles.placeholderImage}>
            <Icon name="image" size={40} color="#bdc3c7" />
          </View>
        )}
      </View>

      <View style={styles.itemContent}>
        <Text style={styles.productName} numberOfLines={1}>
          {item.product_name || 'Unknown Product'}
        </Text>
        <Text style={styles.timestamp}>{formatDate(item.timestamp)}</Text>
        <View style={styles.ingredientCount}>
          <Icon name="list" size={14} color="#7f8c8d" />
          <Text style={styles.ingredientCountText}>
            {item.normalized_ingredients?.length || 0} ingredients
          </Text>
        </View>
      </View>

      <View
        style={[
          styles.verdictBadge,
          {backgroundColor: getVerdictColor(item.verdict)},
        ]}>
        <Icon name={getVerdictIcon(item.verdict)} size={24} color="#fff" />
        <Text style={styles.verdictBadgeText}>{item.verdict}</Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      {history.length === 0 ? (
        <View style={styles.emptyState}>
          <Icon name="history" size={80} color="#bdc3c7" />
          <Text style={styles.emptyStateText}>No scan history yet</Text>
          <Text style={styles.emptyStateSubtext}>
            Your scanned products will appear here
          </Text>
        </View>
      ) : (
        <FlatList
          data={history}
          renderItem={renderItem}
          keyExtractor={(item, index) => item.scan_id || index.toString()}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
          }
        />
      )}

      {showResults && selectedItem && (
        <ResultsModal
          visible={showResults}
          result={selectedItem}
          onClose={handleCloseResults}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f6fa',
  },
  listContent: {
    padding: 12,
  },
  historyItem: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    marginBottom: 12,
    borderRadius: 12,
    overflow: 'hidden',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 1},
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  imageContainer: {
    width: 80,
    height: 80,
  },
  thumbnail: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  placeholderImage: {
    width: '100%',
    height: '100%',
    backgroundColor: '#ecf0f1',
    justifyContent: 'center',
    alignItems: 'center',
  },
  itemContent: {
    flex: 1,
    padding: 12,
    justifyContent: 'center',
  },
  productName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 4,
  },
  timestamp: {
    fontSize: 12,
    color: '#7f8c8d',
    marginBottom: 4,
  },
  ingredientCount: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  ingredientCountText: {
    fontSize: 12,
    color: '#7f8c8d',
    marginLeft: 4,
  },
  verdictBadge: {
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 12,
    minWidth: 80,
  },
  verdictBadgeText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#fff',
    marginTop: 4,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyStateText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#7f8c8d',
    marginTop: 16,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#95a5a6',
    marginTop: 8,
    textAlign: 'center',
  },
});

export default HistoryScreen;
