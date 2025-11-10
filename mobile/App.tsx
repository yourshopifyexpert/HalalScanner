/**
 * HalalScanner Mobile App
 * Main entry point
 */

import React from 'react';
import {SafeAreaProvider} from 'react-native-safe-area-context';
import {NavigationContainer} from '@react-navigation/native';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialIcons';

// Screens
import ScanScreen from './src/screens/ScanScreen';
import HistoryScreen from './src/screens/HistoryScreen';
import SettingsScreen from './src/screens/SettingsScreen';

const Tab = createBottomTabNavigator();

const App = () => {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Tab.Navigator
          screenOptions={({route}) => ({
            tabBarIcon: ({focused, color, size}) => {
              let iconName = 'camera';

              if (route.name === 'Scan') {
                iconName = 'camera-alt';
              } else if (route.name === 'History') {
                iconName = 'history';
              } else if (route.name === 'Settings') {
                iconName = 'settings';
              }

              return <Icon name={iconName} size={size} color={color} />;
            },
            tabBarActiveTintColor: '#27ae60',
            tabBarInactiveTintColor: 'gray',
            headerStyle: {
              backgroundColor: '#27ae60',
            },
            headerTintColor: '#fff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          })}>
          <Tab.Screen
            name="Scan"
            component={ScanScreen}
            options={{title: 'Scan Product'}}
          />
          <Tab.Screen
            name="History"
            component={HistoryScreen}
            options={{title: 'Scan History'}}
          />
          <Tab.Screen
            name="Settings"
            component={SettingsScreen}
            options={{title: 'Settings'}}
          />
        </Tab.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
};

export default App;
