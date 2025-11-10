import React, {useEffect, useState} from 'react';
import {
  Box,
  Card,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const UncertainItems = () => {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUncertainItems();
  }, []);

  const fetchUncertainItems = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/admin/uncertain`);
      setItems(response.data);
    } catch (error) {
      console.error('Failed to fetch uncertain items:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Uncertain Items Requiring Review
      </Typography>

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Product</TableCell>
                <TableCell>Verdict</TableCell>
                <TableCell>Confidence</TableCell>
                <TableCell>Ambiguous Ingredients</TableCell>
                <TableCell>Scan Count</TableCell>
                <TableCell>Date</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map(item => (
                <TableRow key={item.scan_id}>
                  <TableCell>{item.product_name}</TableCell>
                  <TableCell>
                    <Chip
                      label={item.verdict}
                      color={item.verdict === 'SUSPICIOUS' ? 'warning' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {(item.confidence * 100).toFixed(0)}%
                  </TableCell>
                  <TableCell>
                    <Box sx={{display: 'flex', flexWrap: 'wrap', gap: 0.5}}>
                      {item.ambiguous_ingredients.slice(0, 3).map((ing: string, idx: number) => (
                        <Chip key={idx} label={ing} size="small" />
                      ))}
                      {item.ambiguous_ingredients.length > 3 && (
                        <Chip
                          label={`+${item.ambiguous_ingredients.length - 3}`}
                          size="small"
                        />
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>{item.scan_count}</TableCell>
                  <TableCell>{formatDate(item.scan_date)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>
    </Box>
  );
};

export default UncertainItems;
