/**
 * Results Modal - Display scan results
 */

import React, {useState} from 'react';
import {
  Modal,
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {submitFeedback, contactManufacturer} from '../config/api';

interface ResultsModalProps {
  visible: boolean;
  result: any;
  onClose: () => void;
}

const ResultsModal: React.FC<ResultsModalProps> = ({
  visible,
  result,
  onClose,
}) => {
  const [expanded, setExpanded] = useState(false);

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

  const handleAgreeFeedback = async (agree: boolean) => {
    try {
      await submitFeedback(result.scan_id, agree);
      Alert.alert('Thank you!', 'Your feedback helps us improve.');
    } catch (error) {
      Alert.alert('Error', 'Failed to submit feedback');
    }
  };

  const handleContactManufacturer = async () => {
    if (!result.product_id) {
      Alert.alert('Error', 'Product information not available');
      return;
    }

    Alert.alert(
      'Contact Manufacturer',
      'We will send an inquiry to the manufacturer on your behalf.',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Send',
          onPress: async () => {
            try {
              await contactManufacturer(result.scan_id, result.product_id);
              Alert.alert(
                'Success',
                'Inquiry sent to manufacturer. We will notify you when we receive a response.',
              );
            } catch (error) {
              Alert.alert('Error', 'Failed to send inquiry');
            }
          },
        },
      ],
    );
  };

  return (
    <Modal visible={visible} animationType="slide" transparent={false}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Scan Result</Text>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Icon name="close" size={28} color="#2c3e50" />
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.content}>
          {/* Verdict Badge */}
          <View
            style={[
              styles.verdictBadge,
              {backgroundColor: getVerdictColor(result.verdict)},
            ]}>
            <Icon
              name={getVerdictIcon(result.verdict)}
              size={60}
              color="#fff"
            />
            <Text style={styles.verdictText}>{result.verdict}</Text>
            <Text style={styles.confidenceText}>
              Confidence: {(result.confidence * 100).toFixed(0)}%
            </Text>
          </View>

          {/* Product Info */}
          {result.product_name && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Product</Text>
              <Text style={styles.productName}>{result.product_name}</Text>
              {result.barcode && (
                <Text style={styles.barcode}>Barcode: {result.barcode}</Text>
              )}
            </View>
          )}

          {/* Ingredients */}
          <View style={styles.section}>
            <TouchableOpacity
              style={styles.expandHeader}
              onPress={() => setExpanded(!expanded)}>
              <Text style={styles.sectionTitle}>
                Ingredients ({result.normalized_ingredients?.length || 0})
              </Text>
              <Icon
                name={expanded ? 'expand-less' : 'expand-more'}
                size={24}
                color="#2c3e50"
              />
            </TouchableOpacity>

            {expanded && (
              <View style={styles.ingredientsList}>
                {result.normalized_ingredients?.map(
                  (ing: string, index: number) => (
                    <Text key={index} style={styles.ingredient}>
                      • {ing}
                    </Text>
                  ),
                )}
              </View>
            )}
          </View>

          {/* Evidence */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Evidence</Text>
            {result.explanation?.map((evidence: any, index: number) => (
              <View
                key={index}
                style={[
                  styles.evidenceCard,
                  {
                    borderLeftColor:
                      evidence.status === 'HARAM'
                        ? '#e74c3c'
                        : evidence.status === 'AMBIGUOUS'
                        ? '#f39c12'
                        : '#27ae60',
                  },
                ]}>
                <Text style={styles.evidenceIngredient}>
                  {evidence.ingredient}
                </Text>
                <Text style={styles.evidenceStatus}>
                  Status: {evidence.status}
                </Text>
                <Text style={styles.evidenceReason}>{evidence.reason}</Text>
              </View>
            ))}
          </View>

          {/* Suggested Actions */}
          {result.suggested_actions?.length > 0 && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Suggested Actions</Text>
              {result.suggested_actions.map((action: string, index: number) => (
                <Text key={index} style={styles.suggestedAction}>
                  • {action}
                </Text>
              ))}
            </View>
          )}

          {/* Actions */}
          <View style={styles.actionsSection}>
            {result.verdict === 'SUSPICIOUS' && (
              <TouchableOpacity
                style={styles.actionButton}
                onPress={handleContactManufacturer}>
                <Icon name="email" size={20} color="#fff" />
                <Text style={styles.actionButtonText}>
                  Ask Manufacturer
                </Text>
              </TouchableOpacity>
            )}
          </View>

          {/* Feedback */}
          <View style={styles.feedbackSection}>
            <Text style={styles.feedbackTitle}>Was this helpful?</Text>
            <View style={styles.feedbackButtons}>
              <TouchableOpacity
                style={styles.feedbackButton}
                onPress={() => handleAgreeFeedback(true)}>
                <Icon name="thumb-up" size={20} color="#27ae60" />
                <Text style={styles.feedbackButtonText}>Yes</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.feedbackButton}
                onPress={() => handleAgreeFeedback(false)}>
                <Icon name="thumb-down" size={20} color="#e74c3c" />
                <Text style={styles.feedbackButtonText}>No</Text>
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f6fa',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2c3e50',
  },
  closeButton: {
    padding: 4,
  },
  content: {
    flex: 1,
  },
  verdictBadge: {
    alignItems: 'center',
    padding: 30,
    margin: 20,
    borderRadius: 16,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.2,
    shadowRadius: 4,
  },
  verdictText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 12,
  },
  confidenceText: {
    fontSize: 16,
    color: '#fff',
    marginTop: 8,
    opacity: 0.9,
  },
  section: {
    backgroundColor: '#fff',
    margin: 12,
    padding: 16,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 1},
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 12,
  },
  productName: {
    fontSize: 16,
    color: '#2c3e50',
    fontWeight: '500',
  },
  barcode: {
    fontSize: 14,
    color: '#7f8c8d',
    marginTop: 4,
  },
  expandHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  ingredientsList: {
    marginTop: 8,
  },
  ingredient: {
    fontSize: 14,
    color: '#2c3e50',
    marginBottom: 4,
    lineHeight: 20,
  },
  evidenceCard: {
    borderLeftWidth: 4,
    paddingLeft: 12,
    paddingVertical: 8,
    marginBottom: 12,
    backgroundColor: '#f8f9fa',
    borderRadius: 4,
  },
  evidenceIngredient: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 4,
  },
  evidenceStatus: {
    fontSize: 14,
    color: '#7f8c8d',
    marginBottom: 2,
  },
  evidenceReason: {
    fontSize: 14,
    color: '#34495e',
    lineHeight: 18,
  },
  suggestedAction: {
    fontSize: 14,
    color: '#2c3e50',
    marginBottom: 6,
    lineHeight: 20,
  },
  actionsSection: {
    margin: 12,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#3498db',
    padding: 16,
    borderRadius: 12,
    marginBottom: 8,
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  feedbackSection: {
    margin: 12,
    padding: 16,
    backgroundColor: '#fff',
    borderRadius: 12,
  },
  feedbackTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 12,
    textAlign: 'center',
  },
  feedbackButtons: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 16,
  },
  feedbackButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    backgroundColor: '#f8f9fa',
  },
  feedbackButtonText: {
    fontSize: 14,
    color: '#2c3e50',
    marginLeft: 8,
  },
});

export default ResultsModal;
