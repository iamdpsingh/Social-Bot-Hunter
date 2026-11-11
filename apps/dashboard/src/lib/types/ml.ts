export interface MLFeatureAttribution {
  feature_name: string;
  feature_value: number;
  contribution: number;
  relative_weight: number;
  is_missing: boolean;
  explanation: string;
}

export interface MLPredictResult {
  account_id: string;
  bot_probability: number;
  is_bot: boolean;
  risk_band: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
  raw_score: number;
  top_positive_drivers: MLFeatureAttribution[];
  top_negative_drivers: MLFeatureAttribution[];
  missing_feature_count: number;
  model_version: string;
}

export interface MLModelInfo {
  model_version: string;
  algorithm: string;
  trained_at: string;
  training_samples: number;
  metrics: {
    f1?: number;
    pr_auc?: number;
    roc_auc?: number;
    brier_score?: number;
    ece?: number;
    accuracy?: number;
    [key: string]: number | undefined;
  };
  feature_count: number;
  sha256_checksum: string;
  author: string;
  description: string;
}

export interface CalibrationPoint {
  bin_index: number;
  mean_predicted_prob: number;
  fraction_positives: number;
  sample_count: number;
}

export interface CalibrationCurve {
  model_version: string;
  points: CalibrationPoint[];
  ece: number;
  brier_score: number;
}
