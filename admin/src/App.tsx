/**
 * HalalScanner Admin Console
 */

import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  Navigate,
} from 'react-router-dom';
import {
  AppBar,
  Box,
  CssBaseline,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  ThemeProvider,
  createTheme,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Rule as RuleIcon,
  Warning as WarningIcon,
  Business as BusinessIcon,
  Inventory as InventoryIcon,
} from '@mui/icons-material';

// Pages
import Dashboard from './pages/Dashboard';
import Rules from './pages/Rules';
import UncertainItems from './pages/UncertainItems';
import Ingredients from './pages/Ingredients';
import Manufacturers from './pages/Manufacturers';

const drawerWidth = 240;

const theme = createTheme({
  palette: {
    primary: {
      main: '#27ae60',
    },
    secondary: {
      main: '#3498db',
    },
  },
});

function App() {
  const menuItems = [
    {text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard'},
    {text: 'Rules', icon: <RuleIcon />, path: '/rules'},
    {text: 'Uncertain Items', icon: <WarningIcon />, path: '/uncertain'},
    {text: 'Ingredients', icon: <InventoryIcon />, path: '/ingredients'},
    {text: 'Manufacturers', icon: <BusinessIcon />, path: '/manufacturers'},
  ];

  return (
    <ThemeProvider theme={theme}>
      <Router>
        <Box sx={{display: 'flex'}}>
          <CssBaseline />
          <AppBar
            position="fixed"
            sx={{zIndex: theme => theme.zIndex.drawer + 1}}>
            <Toolbar>
              <Typography variant="h6" noWrap component="div">
                HalalScanner Admin Console
              </Typography>
            </Toolbar>
          </AppBar>
          <Drawer
            variant="permanent"
            sx={{
              width: drawerWidth,
              flexShrink: 0,
              '& .MuiDrawer-paper': {
                width: drawerWidth,
                boxSizing: 'border-box',
              },
            }}>
            <Toolbar />
            <Box sx={{overflow: 'auto'}}>
              <List>
                {menuItems.map(item => (
                  <ListItem key={item.text} disablePadding>
                    <ListItemButton component={Link} to={item.path}>
                      <ListItemIcon>{item.icon}</ListItemIcon>
                      <ListItemText primary={item.text} />
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
            </Box>
          </Drawer>
          <Box component="main" sx={{flexGrow: 1, p: 3}}>
            <Toolbar />
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/rules" element={<Rules />} />
              <Route path="/uncertain" element={<UncertainItems />} />
              <Route path="/ingredients" element={<Ingredients />} />
              <Route path="/manufacturers" element={<Manufacturers />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
