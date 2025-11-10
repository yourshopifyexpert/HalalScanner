import React, {useEffect, useState} from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {Edit, Delete, Add} from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const Rules = () => {
  const [rules, setRules] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingRule, setEditingRule] = useState<any>(null);

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/admin/rules`);
      setRules(response.data);
    } catch (error) {
      console.error('Failed to fetch rules:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddRule = () => {
    setEditingRule({
      rule_name: '',
      rule_type: 'blacklist',
      pattern: '',
      verdict: 'HARAM',
      confidence: 0.99,
      reason: '',
      priority: 50,
      active: true,
    });
    setOpenDialog(true);
  };

  const handleEditRule = (rule: any) => {
    setEditingRule(rule);
    setOpenDialog(true);
  };

  const handleSaveRule = async () => {
    try {
      if (editingRule.id) {
        // Update existing rule
        await axios.put(
          `${API_BASE_URL}/admin/rules/${editingRule.id}`,
          editingRule,
        );
      } else {
        // Create new rule
        await axios.post(`${API_BASE_URL}/admin/rules`, editingRule);
      }
      setOpenDialog(false);
      fetchRules();
    } catch (error) {
      console.error('Failed to save rule:', error);
    }
  };

  const handleDeleteRule = async (ruleId: number) => {
    if (window.confirm('Are you sure you want to delete this rule?')) {
      try {
        await axios.delete(`${API_BASE_URL}/admin/rules/${ruleId}`);
        fetchRules();
      } catch (error) {
        console.error('Failed to delete rule:', error);
      }
    }
  };

  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'HALAL':
        return 'success';
      case 'HARAM':
        return 'error';
      case 'SUSPICIOUS':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{display: 'flex', justifyContent: 'space-between', mb: 3}}>
        <Typography variant="h4">Classification Rules</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleAddRule}>
          Add Rule
        </Button>
      </Box>

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Rule Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Pattern</TableCell>
                <TableCell>Verdict</TableCell>
                <TableCell>Priority</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rules.map(rule => (
                <TableRow key={rule.id}>
                  <TableCell>{rule.rule_name}</TableCell>
                  <TableCell>{rule.rule_type}</TableCell>
                  <TableCell sx={{maxWidth: 200, overflow: 'hidden'}}>
                    <code>{rule.pattern}</code>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={rule.verdict}
                      color={getVerdictColor(rule.verdict) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{rule.priority}</TableCell>
                  <TableCell>
                    <Chip
                      label={rule.active ? 'Active' : 'Inactive'}
                      color={rule.active ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton onClick={() => handleEditRule(rule)}>
                      <Edit />
                    </IconButton>
                    <IconButton onClick={() => handleDeleteRule(rule.id)}>
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      {/* Edit/Add Dialog */}
      <Dialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        maxWidth="md"
        fullWidth>
        <DialogTitle>
          {editingRule?.id ? 'Edit Rule' : 'Add New Rule'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{display: 'flex', flexDirection: 'column', gap: 2, mt: 2}}>
            <TextField
              label="Rule Name"
              value={editingRule?.rule_name || ''}
              onChange={e =>
                setEditingRule({...editingRule, rule_name: e.target.value})
              }
              fullWidth
            />
            <FormControl fullWidth>
              <InputLabel>Rule Type</InputLabel>
              <Select
                value={editingRule?.rule_type || 'blacklist'}
                onChange={e =>
                  setEditingRule({...editingRule, rule_type: e.target.value})
                }>
                <MenuItem value="blacklist">Blacklist</MenuItem>
                <MenuItem value="whitelist">Whitelist</MenuItem>
                <MenuItem value="pattern">Pattern</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Pattern (regex)"
              value={editingRule?.pattern || ''}
              onChange={e =>
                setEditingRule({...editingRule, pattern: e.target.value})
              }
              fullWidth
            />
            <FormControl fullWidth>
              <InputLabel>Verdict</InputLabel>
              <Select
                value={editingRule?.verdict || 'HARAM'}
                onChange={e =>
                  setEditingRule({...editingRule, verdict: e.target.value})
                }>
                <MenuItem value="HALAL">HALAL</MenuItem>
                <MenuItem value="HARAM">HARAM</MenuItem>
                <MenuItem value="SUSPICIOUS">SUSPICIOUS</MenuItem>
                <MenuItem value="UNKNOWN">UNKNOWN</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Confidence (0-1)"
              type="number"
              value={editingRule?.confidence || 0.99}
              onChange={e =>
                setEditingRule({
                  ...editingRule,
                  confidence: parseFloat(e.target.value),
                })
              }
              inputProps={{min: 0, max: 1, step: 0.01}}
              fullWidth
            />
            <TextField
              label="Priority"
              type="number"
              value={editingRule?.priority || 50}
              onChange={e =>
                setEditingRule({
                  ...editingRule,
                  priority: parseInt(e.target.value),
                })
              }
              fullWidth
            />
            <TextField
              label="Reason"
              value={editingRule?.reason || ''}
              onChange={e =>
                setEditingRule({...editingRule, reason: e.target.value})
              }
              multiline
              rows={3}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveRule} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Rules;
