import axios, { AxiosInstance, AxiosResponse } from 'axios';

// Simplified types for our current backend
export interface SimplePatient {
  id?: number;
  patient_id: string;
  first_name: string;
  last_name: string;
  age?: number;
  gender?: string;
  phone?: string;
  email?: string;
  address?: string;
  medical_record_number?: string;
  emergency_contact?: {
    name: string;
    phone: string;
    relationship: string;
  };
  insurance_info?: {
    provider: string;
    policy_number: string;
    group_number: string;
  };
  created_at?: string;
  updated_at?: string;
}

export interface SimplePrediction {
  id?: string;
  patient_id: number;
  patient_info?: {
    patient_id: string;
    first_name: string;
    last_name: string;
    age?: number;
    gender?: string;
  };
  image_filename: string;
  prediction: string;
  confidence: number;
  confidence_scores: {
    NORMAL: number;
    PNEUMONIA: number;
  };
  inference_time?: number;
  image_size?: number[];
  created_at?: string;
  notes?: string;
  clinical_notes?: string; // Backend field name
}

export interface PredictionStats {
  total_predictions: number;
  pneumonia_cases: number;
  normal_cases: number;
  unique_patients: number;
  average_confidence: number;
  status: string;
}

export interface PredictionResponse {
  message: string;
  prediction: SimplePrediction;
  status: string;
}

export interface ApiResponse<T = any> {
  message?: string;
  data?: T;
  status: string;
  total?: number;
  items?: SimplePrediction[]; // For paginated responses
  predictions?: SimplePrediction[]; // For backward compatibility
  patient?: SimplePatient;
  page?: number;
  size?: number;
  pages?: number;
}

class SimpleApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Enhanced error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        const message = error.response?.data?.detail || 
                       error.response?.data?.message || 
                       error.message || 
                       'An unexpected error occurred';
        
        console.error('API Error:', error.response?.data || error.message);
        
        return Promise.reject(error);
      }
    );
  }

  private handleSuccess(message: string, data?: any) {
    return data;
  }

  // Health Check
  async healthCheck(): Promise<any> {
    const response = await this.api.get('/api/v1/predictions/health');
    return response.data;
  }

  // Patient Management
  getPatients = async (): Promise<SimplePatient[]> => {
    console.log('=== API Service Debug: getPatients called ===');
    console.log('this.api instance:', this.api);
    try {
      const response: AxiosResponse<{ items: SimplePatient[], total: number, page: number, size: number, pages: number }> = await this.api.get('/api/v1/patients/');
      console.log('Patients API response:', {
        status: response.status,
        data: response.data,
        items: response.data.items,
        itemsLength: response.data.items?.length || 0
      });
      return response.data.items;
    } catch (error) {
      console.error('Patients API error:', error);
      throw error;
    }
  }

  getPatient = async (id: number): Promise<SimplePatient> => {
    const response: AxiosResponse<SimplePatient> = await this.api.get(`/api/v1/patients/${id}`);
    return response.data;
  }

  createPatient = async (patientData: Omit<SimplePatient, 'id' | 'created_at'>): Promise<SimplePatient> => {
    const response: AxiosResponse<SimplePatient> = await this.api.post('/api/v1/patients/', patientData);
    this.handleSuccess(`Patient ${patientData.first_name} ${patientData.last_name} created successfully`);
    return response.data;
  }

  updatePatient = async (id: number, patientData: Omit<SimplePatient, 'id' | 'created_at'>): Promise<SimplePatient> => {
    const response: AxiosResponse<SimplePatient> = await this.api.put(`/api/v1/patients/${id}`, patientData);
    this.handleSuccess(`Patient ${patientData.first_name} ${patientData.last_name} updated successfully`);
    return response.data;
  }

  deletePatient = async (id: number): Promise<{ message: string; patient_id: number }> => {
    const response = await this.api.delete(`/api/v1/patients/${id}`);
    this.handleSuccess('Patient deleted successfully');
    return response.data;
  }

  searchPatients = async (query: string): Promise<SimplePatient[]> => {
    const response: AxiosResponse<SimplePatient[]> = await this.api.get(`/api/v1/patients/search/${encodeURIComponent(query)}`);
    return response.data;
  }

  // Predictions
  createPrediction = async (patientId: number, file: File, notes?: string): Promise<PredictionResponse> => {
    const formData = new FormData();
    formData.append('patient_id', patientId.toString());
    formData.append('file', file);
    if (notes) {
      formData.append('clinical_notes', notes);
    }

    const response: AxiosResponse<PredictionResponse> = await this.api.post(
      '/api/v1/predictions/predict-with-patient',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    
    // Show success message with prediction result
    const prediction = response.data.prediction;
    if (prediction) {
      const result = prediction.prediction === 'PNEUMONIA' ? 'Pneumonia detected' : 'No pneumonia detected';
      const confidence = (prediction.confidence * 100).toFixed(1);
      this.handleSuccess(`Analysis complete: ${result} (${confidence}% confidence)`);
    }
    
    return response.data;
  }

  getAllPredictions = async (): Promise<ApiResponse> => {
    console.log('API: Making request to /api/v1/predictions/predictions');
    console.log('API: this.api instance:', this.api);
    try {
      const response: AxiosResponse<ApiResponse> = await this.api.get('/api/v1/predictions/predictions');
      console.log('API: Response received:', response);
      console.log('API: Response data:', response.data);
      console.log('API: Response status:', response.status);
      return response.data;
    } catch (error: any) {
      console.error('API: Error in getAllPredictions:', error);
      console.error('API: Error response:', error?.response);
      throw error;
    }
  }

  getPatientPredictions = async (patientId: number): Promise<ApiResponse> => {
    const response: AxiosResponse<ApiResponse> = await this.api.get(`/api/v1/predictions/predictions/patient/${patientId}`);
    return response.data;
  }

  getPredictionStats = async (): Promise<PredictionStats> => {
    const response: AxiosResponse<PredictionStats> = await this.api.get('/api/v1/predictions/stats/predictions');
    return response.data;
  }

  // Statistics API
  async getOverviewStats(): Promise<any> {
    console.log('API: Making request to /api/v1/predictions/stats/overview');
    try {
      const response = await this.api.get('/api/v1/predictions/stats/overview');
      console.log('API: Overview stats response:', response.data);
      return response.data;
    } catch (error) {
      console.error('API: Overview stats error:', error);
      throw error;
    }
  }

  async getDailyStats(days: number = 30): Promise<any> {
    const response = await this.api.get(`/api/v1/stats/daily?days=${days}`);
    return response.data;
  }

  async getWeeklyStats(weeks: number = 12): Promise<any> {
    const response = await this.api.get(`/api/v1/stats/weekly?weeks=${weeks}`);
    return response.data;
  }

  async getPatientDemographics(): Promise<any> {
    const response = await this.api.get('/api/v1/stats/patient-demographics');
    return response.data;
  }

  // Audit API
  async getAuditLogs(params?: any): Promise<any> {
    const queryParams = params ? new URLSearchParams(params).toString() : '';
    const response = await this.api.get(`/api/v1/audit/logs?${queryParams}`);
    return response.data;
  }

  async getDashboardStats(): Promise<any> {
    const response = await this.api.get('/api/v1/audit/dashboard/stats');
    return response.data;
  }

  // Export functionality
  exportPredictionsCSV = async (startDate?: string, endDate?: string): Promise<Blob> => {
    console.log('=== Export Predictions CSV Debug ===');
    console.log('Start date:', startDate);
    console.log('End date:', endDate);
    
    try {
      const payload: any = {};
      if (startDate) payload.start_date = startDate;
      if (endDate) payload.end_date = endDate;
      
      console.log('Sending payload:', payload);
      
      const response = await this.api.post('/api/v1/exports/predictions/csv', payload, {
        responseType: 'blob',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      console.log('Export response received, blob size:', response.data.size);
      return response.data;
    } catch (error) {
      console.error('Export predictions CSV error:', error);
      throw error;
    }
  }

  exportPatientsCSV = async (startDate?: string, endDate?: string): Promise<Blob> => {
    console.log('=== Export Patients CSV Debug ===');
    
    try {
      const payload: any = {};
      if (startDate) payload.start_date = startDate;
      if (endDate) payload.end_date = endDate;
      
      const response = await this.api.post('/api/v1/exports/patients/csv', payload, {
        responseType: 'blob',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      return response.data;
    } catch (error) {
      console.error('Export patients CSV error:', error);
      throw error;
    }
  }

  exportPatientsExcel = async (startDate?: string, endDate?: string): Promise<Blob> => {
    try {
      const payload: any = {};
      if (startDate) payload.start_date = startDate;
      if (endDate) payload.end_date = endDate;
      
      const response = await this.api.post('/api/v1/exports/patients/excel', payload, {
        responseType: 'blob',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      return response.data;
    } catch (error) {
      console.error('Export patients Excel error:', error);
      throw error;
    }
  }

  exportPDFReport = async (startDate?: string, endDate?: string): Promise<Blob> => {
    try {
      const payload: any = {};
      if (startDate) payload.start_date = startDate;
      if (endDate) payload.end_date = endDate;
      
      const response = await this.api.post('/api/v1/exports/report/pdf', payload, {
        responseType: 'blob',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      return response.data;
    } catch (error) {
      console.error('Export PDF report error:', error);
      throw error;
    }
  }

  // Simple prediction without patient (for testing)
  async simplePrediction(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.api.post('/api/v1/predictions/predict', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Utility function to download blob as file
  downloadFile = (blob: Blob, filename: string) => {
    console.log('=== Download File Debug ===');
    console.log('Blob size:', blob.size);
    console.log('Filename:', filename);
    
    try {
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      
      // Append to body to ensure it works in all browsers
      document.body.appendChild(link);
      link.click();
      
      // Clean up
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('File download initiated successfully');
    } catch (error) {
      console.error('Error downloading file:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const simpleApiService = new SimpleApiService();
export default simpleApiService;
