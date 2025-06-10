import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Search, 
  Eye,
  Users,
  Phone,
  Mail,
  UserCheck,
  X,
  Loader2,
  Plus,
  Edit,
  Trash2,
  Save,
  UserPlus,
  Activity,
  FileText,
  Clock,
  User
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Skeleton } from '../components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { uzbekTexts } from '../localization/uzbek';
import { simpleApiService, SimplePatient } from '../services/simpleApi';

interface PatientAnalysis {
  id: string;
  prediction: string;
  confidence: number;
  confidence_scores: {
    NORMAL: number;
    PNEUMONIA: number;
  };
  created_at: string;
  reviewed?: boolean;
  reviewed_by?: string;
  clinical_notes?: string;
  image_filename: string;
  inference_time?: number;
  image_size?: number[];
}

const PatientsPage: React.FC = () => {
  const t = uzbekTexts;
  const queryClient = useQueryClient();
  
  // State management
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPatient, setSelectedPatient] = useState<SimplePatient | null>(null);
  const [editingPatient, setEditingPatient] = useState<SimplePatient | null>(null);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [patientToDelete, setPatientToDelete] = useState<SimplePatient | null>(null);
  const [patientAnalyses, setPatientAnalyses] = useState<PatientAnalysis[]>([]);
  const [loadingAnalyses, setLoadingAnalyses] = useState(false);
  
  // Form state for new/editing patient
  const [formData, setFormData] = useState({
    patient_id: '',
    first_name: '',
    last_name: '',
    gender: 'male' as 'male' | 'female',
    age: '',
    phone: '',
    email: '',
    address: ''
  });

  // Form validation errors
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // API queries
  const { data: patients = [], isLoading, error, refetch } = useQuery<SimplePatient[]>({
    queryKey: ['patients'],
    queryFn: async () => {
      try {
        const result = await simpleApiService.getPatients();
        return result;
      } catch (err) {
        throw err;
      }
    },
    retry: 2,
    staleTime: 30000, // 30 seconds
  });

  // Create patient mutation
  const createPatientMutation = useMutation({
    mutationFn: (data: Omit<SimplePatient, 'id' | 'created_at'>) => {
      return simpleApiService.createPatient(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patients'] });
      setShowAddDialog(false);
      resetForm();
    },
    onError: (error) => {
      // Handle error appropriately in production
    }
  });

  // Update patient mutation
  const updatePatientMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Omit<SimplePatient, 'id' | 'created_at'> }) => {
      return simpleApiService.updatePatient(id, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patients'] });
      setEditingPatient(null);
      resetForm();
    },
    onError: (error) => {
      // Handle error appropriately in production
    }
  });

  // Delete patient mutation
  const deletePatientMutation = useMutation({
    mutationFn: (id: number) => {
      return simpleApiService.deletePatient(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patients'] });
      setShowDeleteDialog(false);
      setPatientToDelete(null);
    },
    onError: (error) => {
      // Handle error appropriately in production
    }
  });

  // Form handling functions
  const resetForm = () => {
    setFormData({
      patient_id: '',
      first_name: '',
      last_name: '',
      gender: 'male',
      age: '',
      phone: '',
      email: '',
      address: ''
    });
    setFormErrors({});
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    
    if (!formData.patient_id.trim()) {
      errors.patient_id = t.forms.validation.required;
    }
    if (!formData.first_name.trim()) {
      errors.first_name = t.forms.validation.required;
    }
    if (!formData.last_name.trim()) {
      errors.last_name = t.forms.validation.required;
    }
    if (formData.email && !/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = t.forms.validation.invalidEmail;
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = () => {
    if (!validateForm()) return;
    
    const patientData = {
      ...formData,
      age: formData.age ? parseInt(formData.age) : undefined
    };
    
    if (editingPatient && editingPatient.id) {
      updatePatientMutation.mutate({ 
        id: editingPatient.id, 
        data: patientData as Omit<SimplePatient, 'id' | 'created_at'>
      });
    } else {
      createPatientMutation.mutate(patientData as Omit<SimplePatient, 'id' | 'created_at'>);
    }
  };

  const handleEdit = (patient: SimplePatient) => {
    setEditingPatient(patient);
    setFormData({
      patient_id: patient.patient_id,
      first_name: patient.first_name,
      last_name: patient.last_name,
      gender: (patient.gender === 'male' || patient.gender === 'female') ? patient.gender : 'male',
      age: patient.age?.toString() || '',
      phone: patient.phone || '',
      email: patient.email || '',
      address: patient.address || ''
    });
  };

  const handleDelete = (patient: SimplePatient) => {
    setPatientToDelete(patient);
    setShowDeleteDialog(true);
  };

  const confirmDelete = () => {
    if (patientToDelete?.id) {
      deletePatientMutation.mutate(patientToDelete.id);
    }
  };

  // Filter patients based on search term
  const filteredPatients = patients.filter(patient => {
    const searchLower = searchTerm.toLowerCase();
    return (
      patient.first_name.toLowerCase().includes(searchLower) ||
      patient.last_name.toLowerCase().includes(searchLower) ||
      patient.patient_id.toLowerCase().includes(searchLower) ||
      (patient.phone && patient.phone.toLowerCase().includes(searchLower)) ||
      (patient.email && patient.email.toLowerCase().includes(searchLower))
    );
  });

  const handleViewPatient = (patient: SimplePatient) => {
    setSelectedPatient(patient);
  };

  const closePatientModal = () => {
    setSelectedPatient(null);
    setPatientAnalyses([]);
  };

  // Function to fetch patient analyses
  const fetchPatientAnalyses = async (patientId: number) => {
    setLoadingAnalyses(true);
    try {
      const response = await simpleApiService.getPatientPredictions(patientId);
      const analyses = (response.items || response.predictions || []).map(item => ({
        id: item.id || '',
        prediction: item.prediction,
        confidence: item.confidence,
        confidence_scores: item.confidence_scores,
        created_at: item.created_at || '',
        reviewed: false, // SimplePrediction doesn't have reviewed field yet
        reviewed_by: undefined,
        clinical_notes: item.clinical_notes || item.notes,
        image_filename: item.image_filename,
        inference_time: item.inference_time,
        image_size: item.image_size
      }));
      setPatientAnalyses(analyses);
    } catch (error) {
      console.error('Error fetching patient analyses:', error);
      setPatientAnalyses([]);
    } finally {
      setLoadingAnalyses(false);
    }
  };

  // Update handleViewPatient to fetch analyses
  const handleViewPatientWithAnalyses = (patient: SimplePatient) => {
    setSelectedPatient(patient);
    if (patient.id) {
      fetchPatientAnalyses(patient.id);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-64">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p>{t.common.loading}</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="text-center text-red-600">
              <p className="font-medium">{t.common.error}</p>
              <p className="text-sm mt-1">
                {error instanceof Error ? error.message : 'An error occurred while loading patients'}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
            <Users className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{t.patients.title}</h1>
              <p className="text-gray-600">{t.patients.subtitle}</p>
            </div>
          </div>
          <Button
            onClick={() => {
              resetForm();
              setShowAddDialog(true);
            }}
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            {t.patients.addPatient}
          </Button>
        </div>
      </div>

      {/* Search and Controls */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder={t.common.search}
                className="pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="text-sm text-gray-500">
              {filteredPatients.length} / {patients.length} {t.patients.title.toLowerCase()}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Patients Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          // Loading skeleton cards
          Array.from({ length: 6 }).map((_, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <Skeleton className="h-5 w-32 mb-2" />
                    <Skeleton className="h-4 w-20" />
                  </div>
                  <Skeleton className="h-6 w-16 rounded-full" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 mb-4">
                  <div className="flex items-center gap-2">
                    <Skeleton className="h-4 w-4" />
                    <Skeleton className="h-4 w-24" />
                  </div>
                  <div className="flex items-center gap-2">
                    <Skeleton className="h-4 w-4" />
                    <Skeleton className="h-4 w-32" />
                  </div>
                </div>
                <div className="flex gap-2">
                  <Skeleton className="h-8 flex-1" />
                  <Skeleton className="h-8 w-8" />
                  <Skeleton className="h-8 w-8" />
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          // Actual patient cards
          filteredPatients.map((patient) => (
            <Card key={patient.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">
                      {patient.first_name} {patient.last_name}
                    </CardTitle>
                    <CardDescription className="mt-1">
                      ID: {patient.patient_id}
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-1">
                    <UserCheck className="h-4 w-4 text-green-500" />
                    <span className="text-xs text-green-600 font-medium">
                      {patient.gender === 'male' ? t.patients.male : t.patients.female}
                    </span>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 mb-4">
                  {patient.phone && (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Phone className="h-4 w-4" />
                      <span>{patient.phone}</span>
                    </div>
                  )}
                  {patient.email && (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Mail className="h-4 w-4" />
                      <span className="truncate">{patient.email}</span>
                    </div>
                  )}
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleViewPatientWithAnalyses(patient)}
                    className="flex-1"
                  >
                    <Eye className="h-4 w-4 mr-1" />
                    {t.common.view}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleEdit(patient)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDelete(patient)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Empty State */}
      {filteredPatients.length === 0 && patients.length > 0 && (
        <Card className="mt-8">
          <CardContent className="pt-8 pb-8">
            <div className="text-center text-gray-500">
              <Search className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium mb-2">No results found</p>
              <p>Try adjusting your search terms</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* No Patients State */}
      {patients.length === 0 && !isLoading && (
        <Card className="mt-8">
          <CardContent className="pt-8 pb-8">
            <div className="text-center text-gray-500">
              <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium mb-2">No patients found</p>
              <p>Start by adding your first patient</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Patient Detail Modal */}
      {selectedPatient && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b">
              <div>
                <h2 className="text-xl font-semibold">
                  {selectedPatient.first_name} {selectedPatient.last_name}
                </h2>
                <p className="text-sm text-gray-500">Bemor tafsilotlari va tahlillari</p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={closePatientModal}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="p-6">
              <Tabs defaultValue="info" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="info" className="flex items-center space-x-2">
                    <User size={16} />
                    <span>Ma'lumotlar</span>
                  </TabsTrigger>
                  <TabsTrigger value="analyses" className="flex items-center space-x-2">
                    <Activity size={16} />
                    <span>{t.predictions.patientAnalyses}</span>
                  </TabsTrigger>
                </TabsList>
                
                {/* Patient Info Tab */}
                <TabsContent value="info" className="space-y-4 mt-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Patient ID</Label>
                      <p className="text-sm font-medium">{selectedPatient.patient_id}</p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Gender</Label>
                      <p className="text-sm">{selectedPatient.gender === 'male' ? t.patients.male : t.patients.female}</p>
                    </div>
                    {selectedPatient.age && (
                      <div>
                        <Label className="text-sm font-medium text-gray-500">Age</Label>
                        <p className="text-sm">{selectedPatient.age}</p>
                      </div>
                    )}
                    {selectedPatient.phone && (
                      <div>
                        <Label className="text-sm font-medium text-gray-500">Phone</Label>
                        <p className="text-sm">{selectedPatient.phone}</p>
                      </div>
                    )}
                    {selectedPatient.email && (
                      <div>
                        <Label className="text-sm font-medium text-gray-500">Email</Label>
                        <p className="text-sm">{selectedPatient.email}</p>
                      </div>
                    )}
                    {selectedPatient.address && (
                      <div>
                        <Label className="text-sm font-medium text-gray-500">Address</Label>
                        <p className="text-sm">{selectedPatient.address}</p>
                      </div>
                    )}
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-500">Created</Label>
                    <p className="text-sm">{selectedPatient.created_at ? new Date(selectedPatient.created_at).toLocaleDateString() : 'N/A'}</p>
                  </div>
                </TabsContent>
                
                {/* Patient Analyses Tab */}
                <TabsContent value="analyses" className="space-y-4 mt-6">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium">{t.predictions.patientAnalyses}</h3>
                    <div className="flex items-center space-x-2 text-sm text-gray-500">
                      <Activity size={16} />
                      <span>{patientAnalyses.length} tahlil</span>
                    </div>
                  </div>
                  
                  {loadingAnalyses ? (
                    <div className="flex items-center justify-center py-8">
                      <div className="text-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                        <p className="text-sm text-gray-500">{t.predictions.loadingAnalyses}</p>
                      </div>
                    </div>
                  ) : patientAnalyses.length === 0 ? (
                    <Card>
                      <CardContent className="p-8 text-center">
                        <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                          {t.predictions.noAnalyses}
                        </h3>
                        <p className="text-gray-500 text-sm">
                          Ushbu bemor uchun hali biron tahlil o'tkazilmagan
                        </p>
                      </CardContent>
                    </Card>
                  ) : (
                    <div className="space-y-3">
                      {patientAnalyses.map((analysis) => (
                        <Card key={analysis.id} className="border border-gray-200 hover:border-gray-300 transition-colors">
                          <CardContent className="p-4">
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <div className="flex items-center space-x-3 mb-2">
                                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                                    analysis.prediction === 'PNEUMONIA' 
                                      ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300' 
                                      : 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300'
                                  }`}>
                                    {analysis.prediction === 'PNEUMONIA' ? t.predictions.pneumoniaDetected : t.predictions.normal}
                                  </div>
                                  <div className="flex items-center space-x-1 text-sm text-gray-500">
                                    <Clock size={14} />
                                    <span>{new Date(analysis.created_at).toLocaleDateString('uz-UZ')}</span>
                                  </div>
                                </div>
                                
                                <div className="grid grid-cols-2 gap-4 text-sm">
                                  <div>
                                    <Label className="text-xs font-medium text-gray-500">{t.predictions.confidence}</Label>
                                    <p className="text-sm font-medium">
                                      {(analysis.confidence * 100).toFixed(1)}%
                                    </p>
                                  </div>
                                  <div>
                                    <Label className="text-xs font-medium text-gray-500">Rasm</Label>
                                    <p className="text-sm text-blue-600 dark:text-blue-400">
                                      {analysis.image_filename}
                                    </p>
                                  </div>
                                </div>
                                
                                {analysis.clinical_notes && (
                                  <div className="mt-3">
                                    <Label className="text-xs font-medium text-gray-500">{t.predictions.clinicalNotes}</Label>
                                    <p className="text-sm bg-gray-50 dark:bg-gray-700 p-2 rounded mt-1">
                                      {analysis.clinical_notes}
                                    </p>
                                  </div>
                                )}
                              </div>
                              
                              <Button
                                variant="ghost"
                                size="sm"
                                className="ml-4"
                                onClick={() => {
                                  // TODO: Navigate to prediction details or show full analysis
                                  console.log('View analysis:', analysis.id);
                                }}
                              >
                                <Eye size={16} />
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </div>
          </div>
        </div>
      )}

      {/* Add/Edit Patient Dialog */}
      <Dialog open={showAddDialog || editingPatient !== null} onOpenChange={(open) => {
        if (!open) {
          setShowAddDialog(false);
          setEditingPatient(null);
          resetForm();
        }
      }}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>
              {editingPatient ? t.forms.edit : t.forms.add} {t.patients.title.slice(0, -1)}
            </DialogTitle>
            <DialogDescription>
              {editingPatient ? 'Update patient information' : 'Add a new patient to the system'}
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="patient_id" className="text-right">
                Patient ID
              </Label>
              <div className="col-span-3">
                <Input
                  id="patient_id"
                  value={formData.patient_id}
                  onChange={(e) => setFormData({...formData, patient_id: e.target.value})}
                  placeholder="Enter patient ID"
                />
                {formErrors.patient_id && (
                  <p className="text-sm text-red-600 mt-1">{formErrors.patient_id}</p>
                )}
              </div>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="first_name" className="text-right">
                First Name
              </Label>
              <div className="col-span-3">
                <Input
                  id="first_name"
                  value={formData.first_name}
                  onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                  placeholder="Enter first name"
                />
                {formErrors.first_name && (
                  <p className="text-sm text-red-600 mt-1">{formErrors.first_name}</p>
                )}
              </div>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="last_name" className="text-right">
                Last Name
              </Label>
              <div className="col-span-3">
                <Input
                  id="last_name"
                  value={formData.last_name}
                  onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                  placeholder="Enter last name"
                />
                {formErrors.last_name && (
                  <p className="text-sm text-red-600 mt-1">{formErrors.last_name}</p>
                )}
              </div>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="gender" className="text-right">
                Gender
              </Label>
              <div className="col-span-3">
                <Select value={formData.gender} onValueChange={(value: 'male' | 'female') => setFormData({...formData, gender: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select gender" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="male">{t.patients.male}</SelectItem>
                    <SelectItem value="female">{t.patients.female}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="age" className="text-right">
                Age
              </Label>
              <div className="col-span-3">
                <Input
                  id="age"
                  type="number"
                  value={formData.age}
                  onChange={(e) => setFormData({...formData, age: e.target.value})}
                  placeholder="Enter age"
                />
              </div>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="phone" className="text-right">
                Phone
              </Label>
              <div className="col-span-3">
                <Input
                  id="phone"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  placeholder="Enter phone number"
                />
              </div>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="email" className="text-right">
                Email
              </Label>
              <div className="col-span-3">
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  placeholder="Enter email address"
                />
                {formErrors.email && (
                  <p className="text-sm text-red-600 mt-1">{formErrors.email}</p>
                )}
              </div>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="address" className="text-right">
                Address
              </Label>
              <div className="col-span-3">
                <Input
                  id="address"
                  value={formData.address}
                  onChange={(e) => setFormData({...formData, address: e.target.value})}
                  placeholder="Enter address"
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setShowAddDialog(false);
              setEditingPatient(null);
              resetForm();
            }}>
              {t.forms.cancel}
            </Button>
            <Button 
              onClick={handleSubmit}
              disabled={createPatientMutation.isPending || updatePatientMutation.isPending}
            >
              {(createPatientMutation.isPending || updatePatientMutation.isPending) && (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              )}
              <Save className="h-4 w-4 mr-2" />
              {editingPatient ? t.forms.update : t.forms.save}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Confirm Delete</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete patient "{patientToDelete?.first_name} {patientToDelete?.last_name}"? 
              This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              {t.forms.cancel}
            </Button>
            <Button 
              variant="destructive" 
              onClick={confirmDelete}
              disabled={deletePatientMutation.isPending}
            >
              {deletePatientMutation.isPending && (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              )}
              <Trash2 className="h-4 w-4 mr-2" />
              {t.forms.delete}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default PatientsPage;
