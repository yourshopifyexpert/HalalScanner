/**
 * Settings Screen
 */

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Icon from 'react-native-vector-icons/MaterialIcons';

const SettingsScreen = () => {
  const [privacyMode, setPrivacyMode] = useState(true);
  const [saveHistory, setSaveHistory] = useState(true);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const privacy = await AsyncStorage.getItem('privacyMode');
      const history = await AsyncStorage.getItem('saveHistory');

      if (privacy !== null) {
        setPrivacyMode(JSON.parse(privacy));
      }
      if (history !== null) {
        setSaveHistory(JSON.parse(history));
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const handlePrivacyModeToggle = async (value: boolean) => {
    setPrivacyMode(value);
    await AsyncStorage.setItem('privacyMode', JSON.stringify(value));

    if (value) {
      Alert.alert(
        'Privacy Mode',
        'When enabled, scans are processed locally when possible and images are not uploaded to our servers.',
      );
    }
  };

  const handleSaveHistoryToggle = async (value: boolean) => {
    setSaveHistory(value);
    await AsyncStorage.setItem('saveHistory', JSON.stringify(value));
  };

  const handleClearHistory = () => {
    Alert.alert(
      'Clear History',
      'Are you sure you want to clear all scan history?',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Clear',
          style: 'destructive',
          onPress: async () => {
            await AsyncStorage.removeItem('scanHistory');
            Alert.alert('Success', 'Scan history cleared');
          },
        },
      ],
    );
  };

  const handleAbout = () => {
    Alert.alert(
      'HalalScanner',
      'Version 0.1.0\n\nAI-Powered Halal Product Verification\n\nHelping Muslims make informed choices about food products.',
      [{text: 'OK'}],
    );
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Privacy</Text>

        <View style={styles.settingItem}>
          <View style={styles.settingLeft}>
            <Icon name="security" size={24} color="#27ae60" />
            <View style={styles.settingText}>
              <Text style={styles.settingTitle}>Privacy Mode</Text>
              <Text style={styles.settingDescription}>
                Process scans locally when possible
              </Text>
            </View>
          </View>
          <Switch
            value={privacyMode}
            onValueChange={handlePrivacyModeToggle}
            trackColor={{false: '#ccc', true: '#27ae60'}}
          />
        </View>

        <View style={styles.settingItem}>
          <View style={styles.settingLeft}>
            <Icon name="history" size={24} color="#3498db" />
            <View style={styles.settingText}>
              <Text style={styles.settingTitle}>Save History</Text>
              <Text style={styles.settingDescription}>
                Keep scan history on this device
              </Text>
            </View>
          </View>
          <Switch
            value={saveHistory}
            onValueChange={handleSaveHistoryToggle}
            trackColor={{false: '#ccc', true: '#27ae60'}}
          />
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Data</Text>

        <TouchableOpacity
          style={styles.settingItem}
          onPress={handleClearHistory}>
          <View style={styles.settingLeft}>
            <Icon name="delete" size={24} color="#e74c3c" />
            <View style={styles.settingText}>
              <Text style={styles.settingTitle}>Clear History</Text>
              <Text style={styles.settingDescription}>
                Remove all scan history
              </Text>
            </View>
          </View>
          <Icon name="chevron-right" size={24} color="#bdc3c7" />
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>

        <TouchableOpacity style={styles.settingItem} onPress={handleAbout}>
          <View style={styles.settingLeft}>
            <Icon name="info" size={24} color="#9b59b6" />
            <View style={styles.settingText}>
              <Text style={styles.settingTitle}>About HalalScanner</Text>
              <Text style={styles.settingDescription}>
                Version & information
              </Text>
            </View>
          </View>
          <Icon name="chevron-right" size={24} color="#bdc3c7" />
        </TouchableOpacity>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          HalalScanner helps verify product ingredients
        </Text>
        <Text style={styles.footerSubtext}>
          Always consult with scholars for final rulings
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f6fa',
  },
  section: {
    marginTop: 20,
    backgroundColor: '#fff',
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#7f8c8d',
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 8,
    textTransform: 'uppercase',
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingText: {
    marginLeft: 16,
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#2c3e50',
    marginBottom: 2,
  },
  settingDescription: {
    fontSize: 14,
    color: '#7f8c8d',
  },
  footer: {
    padding: 30,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 14,
    color: '#7f8c8d',
    textAlign: 'center',
    marginBottom: 4,
  },
  footerSubtext: {
    fontSize: 12,
    color: '#95a5a6',
    textAlign: 'center',
  },
});

export default SettingsScreen;
