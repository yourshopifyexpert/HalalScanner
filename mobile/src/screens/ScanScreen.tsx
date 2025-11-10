/**
 * Scan Screen - Camera and image capture
 */

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  ScrollView,
  Image,
} from 'react-native';
import {launchCamera, launchImageLibrary} from 'react-native-image-picker';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {scanProduct} from '../config/api';
import AsyncStorage from '@react-native-async-storage/async-storage';
import ResultsModal from '../components/ResultsModal';

const ScanScreen = ({navigation}: any) => {
  const [loading, setLoading] = useState(false);
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [scanResult, setScanResult] = useState<any>(null);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    // Generate or retrieve user ID
    initializeUser();
  }, []);

  const initializeUser = async () => {
    let userId = await AsyncStorage.getItem('userId');
    if (!userId) {
      userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      await AsyncStorage.setItem('userId', userId);
    }
  };

  const handleTakePhoto = () => {
    launchCamera(
      {
        mediaType: 'photo',
        quality: 0.8,
        includeBase64: true,
        saveToPhotos: false,
      },
      response => {
        if (response.didCancel) {
          return;
        }
        if (response.errorCode) {
          Alert.alert('Error', response.errorMessage || 'Failed to capture image');
          return;
        }
        if (response.assets && response.assets[0]) {
          const asset = response.assets[0];
          setImageUri(asset.uri || null);
          if (asset.base64) {
            processScan(asset.base64);
          }
        }
      },
    );
  };

  const handleChoosePhoto = () => {
    launchImageLibrary(
      {
        mediaType: 'photo',
        quality: 0.8,
        includeBase64: true,
      },
      response => {
        if (response.didCancel) {
          return;
        }
        if (response.errorCode) {
          Alert.alert('Error', response.errorMessage || 'Failed to select image');
          return;
        }
        if (response.assets && response.assets[0]) {
          const asset = response.assets[0];
          setImageUri(asset.uri || null);
          if (asset.base64) {
            processScan(asset.base64);
          }
        }
      },
    );
  };

  const processScan = async (imageBase64: string) => {
    setLoading(true);
    try {
      const result = await scanProduct(imageBase64);
      setScanResult(result);
      setShowResults(true);

      // Save to history
      await saveScanToHistory(result);
    } catch (error: any) {
      Alert.alert(
        'Error',
        error.response?.data?.detail || 'Failed to process scan. Please try again.',
      );
    } finally {
      setLoading(false);
    }
  };

  const saveScanToHistory = async (result: any) => {
    try {
      const history = await AsyncStorage.getItem('scanHistory');
      const historyArray = history ? JSON.parse(history) : [];

      historyArray.unshift({
        ...result,
        imageUri,
        timestamp: new Date().toISOString(),
      });

      // Keep last 50 scans
      if (historyArray.length > 50) {
        historyArray.pop();
      }

      await AsyncStorage.setItem('scanHistory', JSON.stringify(historyArray));
    } catch (error) {
      console.error('Failed to save scan to history:', error);
    }
  };

  const handleCloseResults = () => {
    setShowResults(false);
    setImageUri(null);
    setScanResult(null);
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.title}>Scan Product Label</Text>
          <Text style={styles.subtitle}>
            Take a photo of the ingredients list to check if the product is halal
          </Text>
        </View>

        {imageUri && !loading && (
          <View style={styles.imagePreview}>
            <Image source={{uri: imageUri}} style={styles.image} />
          </View>
        )}

        {loading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#27ae60" />
            <Text style={styles.loadingText}>Analyzing product...</Text>
            <Text style={styles.loadingSubtext}>
              Extracting text and checking ingredients
            </Text>
          </View>
        )}

        {!loading && !imageUri && (
          <View style={styles.instructions}>
            <Icon name="photo-camera" size={80} color="#bdc3c7" />
            <Text style={styles.instructionText}>
              Get started by taking a photo or choosing from gallery
            </Text>
          </View>
        )}
      </ScrollView>

      {!loading && (
        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[styles.button, styles.primaryButton]}
            onPress={handleTakePhoto}>
            <Icon name="camera-alt" size={24} color="#fff" />
            <Text style={styles.buttonText}>Take Photo</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.secondaryButton]}
            onPress={handleChoosePhoto}>
            <Icon name="photo-library" size={24} color="#27ae60" />
            <Text style={[styles.buttonText, styles.secondaryButtonText]}>
              Choose from Gallery
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {showResults && scanResult && (
        <ResultsModal
          visible={showResults}
          result={scanResult}
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
  scrollContent: {
    flexGrow: 1,
  },
  header: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: '#7f8c8d',
    lineHeight: 20,
  },
  imagePreview: {
    margin: 20,
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: '#fff',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  image: {
    width: '100%',
    height: 300,
    resizeMode: 'contain',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 18,
    fontWeight: '600',
    color: '#2c3e50',
  },
  loadingSubtext: {
    marginTop: 8,
    fontSize: 14,
    color: '#7f8c8d',
  },
  instructions: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  instructionText: {
    marginTop: 20,
    fontSize: 16,
    color: '#7f8c8d',
    textAlign: 'center',
    lineHeight: 24,
  },
  buttonContainer: {
    padding: 20,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#ecf0f1',
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  primaryButton: {
    backgroundColor: '#27ae60',
  },
  secondaryButton: {
    backgroundColor: '#fff',
    borderWidth: 2,
    borderColor: '#27ae60',
  },
  buttonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
    marginLeft: 8,
  },
  secondaryButtonText: {
    color: '#27ae60',
  },
});

export default ScanScreen;
