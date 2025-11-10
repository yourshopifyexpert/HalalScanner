import React, {useEffect, useState} from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  CircularProgress,
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Warning,
  Help,
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalScans: 0,
    halalCount: 0,
    haramCount: 0,
    suspiciousCount: 0,
    unknownCount: 0,
  });

  useEffect(() => {
    // Mock data for now
    // TODO: Fetch real stats from API
    setTimeout(() => {
      setStats({
        totalScans: 1247,
        halalCount: 856,
        haramCount: 123,
        suspiciousCount: 198,
        unknownCount: 70,
      });
      setLoading(false);
    }, 500);
  }, []);

  const statCards = [
    {
      title: 'Total Scans',
      value: stats.totalScans,
      icon: <Help sx={{fontSize: 40}} />,
      color: '#3498db',
    },
    {
      title: 'Halal Products',
      value: stats.halalCount,
      icon: <CheckCircle sx={{fontSize: 40}} />,
      color: '#27ae60',
    },
    {
      title: 'Haram Products',
      value: stats.haramCount,
      icon: <Cancel sx={{fontSize: 40}} />,
      color: '#e74c3c',
    },
    {
      title: 'Suspicious Products',
      value: stats.suspiciousCount,
      icon: <Warning sx={{fontSize: 40}} />,
      color: '#f39c12',
    },
  ];

  if (loading) {
    return (
      <Box sx={{display: 'flex', justifyContent: 'center', mt: 4}}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Grid container spacing={3}>
        {statCards.map(card => (
          <Grid item xs={12} sm={6} md={3} key={card.title}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      {card.title}
                    </Typography>
                    <Typography variant="h4">{card.value}</Typography>
                  </Box>
                  <Box sx={{color: card.color}}>{card.icon}</Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box sx={{mt: 4}}>
        <Typography variant="h6" gutterBottom>
          Quick Stats
        </Typography>
        <Card>
          <CardContent>
            <Typography variant="body2" color="textSecondary">
              Success Rate:{' '}
              {((stats.halalCount / stats.totalScans) * 100).toFixed(1)}%
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{mt: 1}}>
              Items Needing Review: {stats.suspiciousCount + stats.unknownCount}
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default Dashboard;
