const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

export const API = {
  HEALTH: `${API_BASE_URL}/health`,
  DETECT: `${API_BASE_URL}/detect`,
  COMPARE_IMAGE: `${API_BASE_URL}/compare-image`,
  MODELS_COMPARISON: `${API_BASE_URL}/models/comparison`,
};

export default API;
