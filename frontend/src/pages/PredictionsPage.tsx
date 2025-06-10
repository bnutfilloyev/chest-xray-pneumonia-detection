import React, { useState, useCallback, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Upload,
  Activity,
  Search,
  CheckCircle,
  AlertCircle,
  Eye,
  Download,
  FileX,
  Users,
  User,
  Calendar,
  Clock,
  TrendingUp,
  AlertTriangle,
  Shield,
  Brain,
  Heart,
  Stethoscope,
  FileImage,
  Zap
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Progress } from '../components/ui/progress';
import { Separator } from '../components/ui/separator';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { Textarea } from '../components/ui/textarea';
import { useToast } from '../components/ui/use-toast';
import { Skeleton } from '../components/ui/skeleton';
import { uzbekTexts } from '../localization/uzbek';
import { simpleApiService, SimplePatient, SimplePrediction } from '../services/simpleApi';

interface UploadedImage {
  file: File;
  preview: string;
  id: string;
}

const PredictionsPage: React.FC = () => {
  const t = uzbekTexts;
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // State management
  const [activeTab, setActiveTab] = useState('upload');
  const [uploadedImages, setUploadedImages] = useState<UploadedImage[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<string>('');
  const [analysisNotes, setAnalysisNotes] = useState('');
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedPrediction, setSelectedPrediction] = useState<SimplePrediction | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  // API Queries
  const { data: patients = [], isLoading: patientsLoading, error: patientsError } = useQuery({
    queryKey: ['patients'],
    queryFn: () => simpleApiService.getPatients(),
    retry: 3,
    retryDelay: 1000,
  });

  const { data: predictionsResponse, isLoading: predictionsLoading, refetch: refetchPredictions, error: predictionsError } = useQuery({
    queryKey: ['predictions'],
    queryFn: () => simpleApiService.getAllPredictions(),
  });

  // Handle both possible response formats from backend
  const predictions = predictionsResponse?.items || predictionsResponse?.predictions || [];

  // Add debug logging
  console.log('PredictionsPage Debug:', {
    predictionsResponse,
    predictionsLoading,
    predictions,
    predictionsLength: predictions.length,
    predictionsError,
    patients,
    patientsLoading,
    selectedPatient,
    patientsLength: patients.length,
    patientsError,
  });

  // Mutations
  const createPredictionMutation = useMutation({
    mutationFn: ({ patientId, file, notes }: { patientId: number; file: File; notes?: string }) => 
      simpleApiService.createPrediction(patientId, file, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['predictions'] });
      toast({
        title: t.predictions.uploadSuccess,
        description: t.predictions.analysisComplete,
      });
      setUploadedImages([]);
      setSelectedPatient('');
      setAnalysisNotes('');
      setActiveTab('results');
    },
    onError: (error) => {
      toast({
        title: t.predictions.uploadError,
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  // Debug handler for patient selection
  const handlePatientChange = (value: string) => {
    console.log('=== PATIENT SELECTION DEBUG ===');
    console.log('Patient selection changed:', { 
      value, 
      previousValue: selectedPatient,
      valueType: typeof value,
      isValidValue: !!value && value !== ''
    });
    
    // Find the selected patient to debug
    const selectedPatientData = patients.find(p => (p.id || p.patient_id).toString() === value);
    console.log('Selected patient data:', selectedPatientData);
    
    setSelectedPatient(value);
    console.log('State should now be updated to:', value);
    console.log('================================');
  };

  // File handling
  const handleFileSelect = useCallback((files: FileList | null) => {
    if (!files) return;

    const newImages: UploadedImage[] = [];
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/dicom'];

    Array.from(files).forEach((file) => {
      // File type validation
      if (!file.type.startsWith('image/')) {
        toast({
          title: 'Noto\'g\'ri fayl turi',
          description: `${file.name} rasm fayli emas`,
          variant: 'destructive',
        });
        return;
      }

      // File size validation
      if (file.size > maxSize) {
        toast({
          title: 'Fayl hajmi katta',
          description: `${file.name} hajmi 10MB dan katta`,
          variant: 'destructive',
        });
        return;
      }

      const id = Math.random().toString(36).substr(2, 9);
      const preview = URL.createObjectURL(file);
      newImages.push({ file, preview, id });
    });

    if (newImages.length > 0) {
      setUploadedImages(prev => [...prev, ...newImages]);
      toast({
        title: 'Muvaffaqiyatli yuklandi',
        description: `${newImages.length} ta rasm yuklandi`,
      });
    }
  }, [toast]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    handleFileSelect(e.dataTransfer.files);
  }, [handleFileSelect]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const removeImage = (id: string) => {
    setUploadedImages(prev => {
      const imageToRemove = prev.find(img => img.id === id);
      if (imageToRemove) {
        URL.revokeObjectURL(imageToRemove.preview);
      }
      return prev.filter(img => img.id !== id);
    });
    
    toast({
      title: 'Rasm o\'chirildi',
      description: 'Tanlangan rasm ro\'yxatdan o\'chirildi',
    });
  };

  // Analysis simulation
  const startAnalysis = async () => {
    // Enhanced validation
    if (uploadedImages.length === 0) {
      toast({
        title: t.forms.validation.required,
        description: "Ko'krak qafasi rentgen rasmini yuklang",
        variant: 'destructive',
      });
      return;
    }

    if (!selectedPatient) {
      toast({
        title: t.forms.validation.required,
        description: "Tahlil uchun bemorni tanlang",
        variant: 'destructive',
      });
      return;
    }

    setIsAnalyzing(true);
    setAnalysisProgress(0);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setAnalysisProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + Math.random() * 15;
      });
    }, 500);

    try {
      // For now, handle one image at a time since the API expects a single file
      const firstImage = uploadedImages[0];
      if (firstImage) {
        await createPredictionMutation.mutateAsync({
          patientId: parseInt(selectedPatient),
          file: firstImage.file,
          notes: analysisNotes
        });
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      toast({
        title: t.predictions.uploadError,
        description: 'Tahlilni qayta ishlashda xatolik yuz berdi',
        variant: 'destructive',
      });
    } finally {
      setIsAnalyzing(false);
      clearInterval(progressInterval);
      setAnalysisProgress(0);
    }
  };

  const getResultBadge = (result: string, confidenceScores?: { NORMAL: number; PNEUMONIA: number }) => {
    // Determine which prediction has higher confidence
    const isPneumoniaHigher = confidenceScores ? 
      confidenceScores.PNEUMONIA > confidenceScores.NORMAL : 
      (result === 'PNEUMONIA' || result === 'pneumonia');
    
    const variant = isPneumoniaHigher ? 'destructive' : 'success';
    const icon = isPneumoniaHigher ? AlertTriangle : Shield;
    const label = isPneumoniaHigher ? t.predictions.pneumoniaDetected : t.predictions.normal;
    
    return (
      <Badge variant={variant} className="flex items-center gap-1">
        {React.createElement(icon, { size: 12 })}
        {label}
      </Badge>
    );
  };

  // Dual-color progress bar component for showing both confidence scores
  const DualConfidenceBar = ({ confidenceScores }: { confidenceScores: { NORMAL: number; PNEUMONIA: number } }) => {
    const normalPercent = (confidenceScores.NORMAL * 100);
    const pneumoniaPercent = (confidenceScores.PNEUMONIA * 100);
    
    return (
      <div className="w-full">
        <div className="flex justify-between text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 bg-emerald-600 rounded-full"></div>
            Normal: {normalPercent.toFixed(1)}%
          </span>
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
            Pneumonia: {pneumoniaPercent.toFixed(1)}%
          </span>
        </div>
        <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden flex">
          <div 
            className="bg-emerald-600 h-full transition-all duration-300"
            style={{ width: `${normalPercent}%` }}
          ></div>
          <div 
            className="bg-blue-600 h-full transition-all duration-300"
            style={{ width: `${pneumoniaPercent}%` }}
          ></div>
        </div>
      </div>
    );
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Noma\'lum sana';
    return new Date(dateString).toLocaleDateString('uz-UZ', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Export functionality
  const handleExportPredictions = async () => {
    try {
      console.log('=== Starting Predictions Export ===');
      
      // Show loading toast
      toast({
        title: 'Ma\'lumotlar eksport qilinmoqda...',
        description: 'Iltimos kuting, fayl tayyorlanmoqda',
      });

      const blob = await simpleApiService.exportPredictionsCSV();
      const filename = `predictions_export_${new Date().toISOString().split('T')[0]}.csv`;
      simpleApiService.downloadFile(blob, filename);
      
      toast({
        title: 'Eksport muvaffaqiyatli bajarildi',
        description: `${filename} fayli yuklab olindi`,
      });
    } catch (error) {
      console.error('Export error:', error);
      toast({
        title: 'Eksport xatosi',
        description: 'Ma\'lumotlarni eksport qilishda xatolik yuz berdi',
        variant: 'destructive',
      });
    }
  };

  const handleExportPatientsExcel = async () => {
    try {
      console.log('=== Starting Patients Excel Export ===');
      
      toast({
        title: 'Excel fayl tayyorlanmoqda...',
        description: 'Iltimos kuting, fayl yaratilmoqda',
      });

      const blob = await simpleApiService.exportPatientsExcel();
      const filename = `patients_export_${new Date().toISOString().split('T')[0]}.xlsx`;
      simpleApiService.downloadFile(blob, filename);
      
      toast({
        title: 'Excel eksport muvaffaqiyatli bajarildi',
        description: `${filename} fayli yuklab olindi`,
      });
    } catch (error) {
      console.error('Excel export error:', error);
      toast({
        title: 'Excel eksport xatosi',
        description: 'Excel faylni yaratishda xatolik yuz berdi',
        variant: 'destructive',
      });
    }
  };

  const handleExportPDFReport = async () => {
    try {
      console.log('=== Starting PDF Report Export ===');
      
      toast({
        title: 'PDF hisobot tayyorlanmoqda...',
        description: 'Iltimos kuting, hisobot yaratilmoqda',
      });

      const blob = await simpleApiService.exportPDFReport();
      const filename = `pneumonia_report_${new Date().toISOString().split('T')[0]}.pdf`;
      simpleApiService.downloadFile(blob, filename);
      
      toast({
        title: 'PDF hisobot tayyor',
        description: `${filename} fayli yuklab olindi`,
      });
    } catch (error) {
      console.error('PDF export error:', error);
      toast({
        title: 'PDF eksport xatosi',
        description: 'PDF hisobotni yaratishda xatolik yuz berdi',
        variant: 'destructive',
      });
    }
  };

  const handleExportPatientsCSV = async () => {
    try {
      console.log('=== Starting Patients CSV Export ===');
      
      toast({
        title: 'Bemorlar ma\'lumotlari eksport qilinmoqda...',
        description: 'Iltimos kuting, CSV fayl tayyorlanmoqda',
      });

      const blob = await simpleApiService.exportPatientsCSV();
      const filename = `patients_export_${new Date().toISOString().split('T')[0]}.csv`;
      simpleApiService.downloadFile(blob, filename);
      
      toast({
        title: 'Bemorlar CSV eksporti tayyor',
        description: `${filename} fayli yuklab olindi`,
      });
    } catch (error) {
      console.error('Patients CSV export error:', error);
      toast({
        title: 'Bemorlar CSV eksport xatosi',
        description: 'Bemorlar ma\'lumotlarini eksport qilishda xatolik yuz berdi',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Activity className="text-purple-600" size={28} />
              {t.navigation.predictions}
            </h1>
            <p className="text-gray-600 mt-1">{t.predictions.description}</p>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                refetchPredictions();
                queryClient.invalidateQueries({ queryKey: ['patients'] });
              }}
              disabled={predictionsLoading}
              className="flex items-center gap-1"
            >
              <TrendingUp size={14} />
              Yangilash
            </Button>
            <Badge variant="secondary" className="flex items-center gap-1">
              <Brain size={12} />
              AI Model v2.1
            </Badge>
            <Badge variant="outline" className="flex items-center gap-1">
              <TrendingUp size={12} />
              98.5% {t.predictions.accuracy}
            </Badge>
          </div>
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="upload" className="flex items-center gap-2">
              <Upload size={16} />
              {t.predictions.newAnalysis}
            </TabsTrigger>
            <TabsTrigger value="results" className="flex items-center gap-2">
              <Activity size={16} />
              {t.predictions.results}
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center gap-2">
              <Clock size={16} />
              {t.predictions.history}
            </TabsTrigger>
          </TabsList>

          {/* Upload Tab */}
          <TabsContent value="upload" className="space-y-6">
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
              {/* Image Upload */}
              <div className="xl:col-span-2">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <FileImage className="text-blue-600" size={20} />
                      {t.predictions.imageUpload}
                    </CardTitle>
                    <CardDescription>{t.predictions.uploadInstructions}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Drop Zone */}
                    <div
                      onDrop={handleDrop}
                      onDragOver={handleDragOver}
                      onDragEnter={handleDragEnter}
                      onDragLeave={handleDragLeave}
                      className={`border-2 border-dashed rounded-lg p-6 lg:p-8 text-center transition-all cursor-pointer focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-offset-2 ${
                        isDragOver 
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/50' 
                          : uploadedImages.length === 0 && selectedPatient
                          ? 'border-red-300 hover:border-red-400 bg-red-50/50'
                          : 'border-gray-300 hover:border-blue-400'
                      }`}
                      onClick={() => fileInputRef.current?.click()}
                      role="button"
                      tabIndex={0}
                      aria-label="Rentgen rasm yuklash maydoni"
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          fileInputRef.current?.click();
                        }
                      }}
                    >
                      <Upload className={`mx-auto mb-4 transition-colors ${
                        isDragOver ? 'text-blue-500' : 
                        uploadedImages.length === 0 && selectedPatient ? 'text-red-400' : 'text-gray-400'
                      }`} size={40} />
                      <p className={`text-base lg:text-lg font-medium mb-2 transition-colors ${
                        isDragOver ? 'text-blue-600' : 
                        uploadedImages.length === 0 && selectedPatient ? 'text-red-600' : 'text-gray-600'
                      }`}>
                        {isDragOver ? 'Fasllarni qo\'yish uchun qo\'yib bering' : t.predictions.dragDrop}
                      </p>
                      <p className="text-xs lg:text-sm text-gray-500 mb-4">
                        {t.predictions.supportedFormats}
                      </p>
                      <Button variant="outline" size="sm" className={isDragOver ? 'border-blue-500 text-blue-600' : ''}>
                        {t.predictions.selectFiles}
                      </Button>
                      {uploadedImages.length === 0 && selectedPatient && (
                        <p className="text-xs text-red-500 flex items-center gap-1 justify-center mt-3">
                          <AlertCircle size={12} />
                          Tahlil uchun rentgen rasm yuklang
                        </p>
                      )}
                    </div>
                    
                    <input
                      ref={fileInputRef}
                      type="file"
                      multiple
                      accept="image/*,.dcm"
                      className="hidden"
                      onChange={(e) => handleFileSelect(e.target.files)}
                      aria-label="Rentgen rasm fayllarini tanlash"
                    />

                    {/* Uploaded Images */}
                    {uploadedImages.length > 0 && (
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <Label className="text-sm font-medium">{t.predictions.uploadedImages}</Label>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              uploadedImages.forEach(img => URL.revokeObjectURL(img.preview));
                              setUploadedImages([]);
                              toast({
                                title: 'Barcha rasmlar o\'chirildi',
                                description: 'Yuklangan rasmlar ro\'yxati tozalandi',
                              });
                            }}
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            <FileX size={14} className="mr-1" />
                            Barchasini o'chirish
                          </Button>
                        </div>
                        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                          {uploadedImages.map((image) => (
                            <div key={image.id} className="relative group">
                              <img
                                src={image.preview}
                                alt="Uploaded"
                                className="w-full h-20 sm:h-24 object-cover rounded-lg border"
                              />
                              <Button
                                variant="destructive"
                                size="sm"
                                className="absolute top-1 right-1 h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                                onClick={() => removeImage(image.id)}
                                aria-label={`Rasmni o'chirish`}
                              >
                                <FileX size={12} />
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Analysis Panel */}
              <div className="space-y-6">
                {/* Patient Selection */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <User className="text-green-600" size={20} />
                      {t.patients.selectPatient}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {patientsLoading ? (
                      <Skeleton className="h-10 w-full" />
                    ) : (
                      <div className="space-y-2">
                        <Select value={selectedPatient} onValueChange={handlePatientChange}>
                          <SelectTrigger className={`${!selectedPatient && uploadedImages.length > 0 ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''}`}>
                            <SelectValue placeholder={t.patients.selectPatient} />
                          </SelectTrigger>
                          <SelectContent className="z-50 max-h-[200px] overflow-y-auto">
                            {patients.length === 0 ? (
                              <SelectItem value="loading" disabled>
                                Bemorlar yuklanmoqda...
                              </SelectItem>
                            ) : (
                              patients.map((patient) => {
                                console.log('Rendering patient:', patient);
                                return (
                                  <SelectItem 
                                    key={patient.id || patient.patient_id} 
                                    value={(patient.id || patient.patient_id).toString()}
                                  >
                                    {patient.first_name} {patient.last_name}
                                  </SelectItem>
                                );
                              })
                            )}
                          </SelectContent>
                        </Select>
                        {!selectedPatient && uploadedImages.length > 0 && (
                          <p className="text-xs text-red-500 flex items-center gap-1">
                            <AlertCircle size={12} />
                            Bemor tanlanishi shart
                          </p>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Analysis Notes */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Stethoscope className="text-purple-600" size={20} />
                      {t.predictions.clinicalNotes}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Textarea
                      placeholder={t.predictions.notesPlaceholder}
                      value={analysisNotes}
                      onChange={(e) => setAnalysisNotes(e.target.value)}
                      className="min-h-[100px]"
                    />
                  </CardContent>
                </Card>

                {/* Analysis Button */}
                <Card>
                  <CardContent className="pt-6">
                    {isAnalyzing ? (
                      <div className="space-y-4">
                        <div className="flex items-center gap-2 text-blue-600">
                          <Zap className="animate-pulse" size={20} />
                          <span className="font-medium">{t.predictions.analyzing}</span>
                        </div>
                        <Progress value={analysisProgress} className="w-full" />
                        <p className="text-sm text-gray-600">
                          {Math.round(analysisProgress)}% {t.predictions.complete}
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        <Button 
                          onClick={startAnalysis}
                          className="w-full"
                          disabled={uploadedImages.length === 0 || !selectedPatient || createPredictionMutation.isPending}
                        >
                          <Brain size={16} className="mr-2" />
                          {createPredictionMutation.isPending ? 'Yuklanmoqda...' : t.predictions.startAnalysis}
                        </Button>
                        
                        {(uploadedImages.length === 0 || !selectedPatient) && (
                          <div className="text-xs text-gray-500 space-y-1">
                            <div className="flex items-center gap-2">
                              <div className={`w-2 h-2 rounded-full ${uploadedImages.length > 0 ? 'bg-green-500' : 'bg-gray-300'}`} />
                              <span>Rasm yuklangan</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <div className={`w-2 h-2 rounded-full ${selectedPatient ? 'bg-green-500' : 'bg-gray-300'}`} />
                              <span>Bemor tanlangan</span>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Results Tab */}
          <TabsContent value="results" className="space-y-6">
            {/* Export Controls */}
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Tahlil natijalari</h3>
                <p className="text-sm text-gray-600">Jami: {predictions.length} ta tahlil</p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" onClick={handleExportPredictions} disabled={predictions.length === 0}>
                  <Download size={16} className="mr-2" />
                  CSV Tahlillar
                </Button>
                <Button variant="outline" onClick={handleExportPatientsCSV} disabled={predictions.length === 0}>
                  <Users size={16} className="mr-2" />
                  CSV Bemorlar
                </Button>
                <Button variant="outline" onClick={handleExportPatientsExcel} disabled={predictions.length === 0}>
                  <FileX size={16} className="mr-2" />
                  Excel
                </Button>
                <Button variant="outline" onClick={handleExportPDFReport} disabled={predictions.length === 0}>
                  <FileImage size={16} className="mr-2" />
                  PDF
                </Button>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {predictionsLoading ? (
                // Loading skeleton cards
                Array.from({ length: 6 }).map((_, index) => (
                  <Card key={index} className="hover:shadow-md transition-shadow">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <Skeleton className="h-5 w-32 mb-2" />
                          <Skeleton className="h-4 w-24" />
                        </div>
                        <Skeleton className="h-6 w-20 rounded-full" />
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <Skeleton className="w-full h-32 rounded-lg" />
                      
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <Skeleton className="h-4 w-16" />
                          <Skeleton className="h-4 w-12" />
                        </div>
                        <div>
                          <Skeleton className="h-4 w-20 mb-1" />
                          <Skeleton className="h-12 w-full rounded" />
                        </div>
                      </div>

                      <Separator />
                      
                      <div className="flex gap-2">
                        <Skeleton className="h-8 flex-1" />
                        <Skeleton className="h-8 w-20" />
                      </div>
                    </CardContent>
                  </Card>
                ))
              ) : predictions.length === 0 ? (
                <div className="col-span-full">
                  <Card>
                    <CardContent className="pt-8 pb-8">
                      <div className="text-center text-gray-500">
                        <Activity className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                        <p className="text-lg font-medium mb-2">Hech qanday tahlil topilmadi</p>
                        <p>Birinchi tahlilni boshlash uchun rasm yuklang</p>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ) : (
                predictions.slice(0, 6).map((prediction) => (
                  <Card key={prediction.id} className="hover:shadow-md transition-shadow">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <CardTitle className="text-lg">
                            {patients.find(p => p.id === prediction.patient_id)?.first_name} {patients.find(p => p.id === prediction.patient_id)?.last_name}
                          </CardTitle>
                          <CardDescription>
                            {formatDate(prediction.created_at)}
                          </CardDescription>
                        </div>
                        {getResultBadge(prediction.prediction, prediction.confidence_scores)}
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="relative">
                        <img
                          src={`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/uploads/predictions/${prediction.image_filename}`}
                          alt="X-ray analysis"
                          className="w-full h-32 object-cover rounded-lg border"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label className="text-sm font-medium">{t.predictions.confidence}</Label>
                        <DualConfidenceBar confidenceScores={prediction.confidence_scores} />
                      </div>

                      {(prediction.notes || prediction.clinical_notes) && (
                        <div>
                          <Label className="text-sm font-medium">{t.predictions.clinicalNotes}</Label>
                          <div className="mt-1 p-3 bg-gray-50 rounded-lg text-sm line-clamp-2">
                            {prediction.notes || prediction.clinical_notes}
                          </div>
                        </div>
                      )}

                      <Separator />
                      
                      <div className="flex flex-col sm:flex-row gap-2">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button variant="outline" size="sm" className="w-full">
                              <Eye size={14} className="mr-1" />
                              {t.common.view}
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="max-w-2xl">
                            <DialogHeader>
                              <DialogTitle>
                                {patients.find(p => p.id === prediction.patient_id)?.first_name} {patients.find(p => p.id === prediction.patient_id)?.last_name} - {t.predictions.analysisDetails}
                              </DialogTitle>
                              <DialogDescription>
                                {formatDate(prediction.created_at)}
                              </DialogDescription>
                            </DialogHeader>
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                              <div>
                                <Label className="text-sm font-medium mb-2 block">X-ray {t.predictions.image}</Label>
                                <img
                                  src={`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/uploads/predictions/${prediction.image_filename}`}
                                  alt="X-ray analysis"
                                  className="w-full h-48 lg:h-64 object-cover rounded-lg border"
                                />
                              </div>
                              <div className="space-y-4">
                                <div>
                                  <Label className="text-sm font-medium">{t.predictions.result}</Label>
                                  <div className="mt-1">
                                    {getResultBadge(prediction.prediction, prediction.confidence_scores)}
                                  </div>
                                </div>
                                
                                <div>
                                  <Label className="text-sm font-medium">{t.predictions.confidence}</Label>
                                  <div className="mt-2">
                                    <DualConfidenceBar confidenceScores={prediction.confidence_scores} />
                                  </div>
                                </div>

                                {(prediction.notes || prediction.clinical_notes) && (
                                  <div>
                                    <Label className="text-sm font-medium">{t.predictions.clinicalNotes}</Label>
                                    <div className="mt-1 p-3 bg-gray-50 rounded-lg text-sm">
                                      {prediction.notes || prediction.clinical_notes}
                                    </div>
                                  </div>
                                )}
                              </div>
                            </div>
                          </DialogContent>
                        </Dialog>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
            
            {predictions.length > 6 && (
              <div className="text-center">
                <Button variant="outline">
                  Ko'proq ko'rish
                </Button>
              </div>
            )}
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="text-blue-600" size={20} />
                  {t.predictions.analysisHistory}
                </CardTitle>
                <CardDescription>
                  {t.predictions.totalAnalyses}: {predictions.length}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {predictions.length > 0 ? (
                  <div className="space-y-3">
                    {predictions.map((prediction) => (
                      <div key={prediction.id} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors gap-3">
                        <div className="flex items-center gap-4">
                          <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                            <Stethoscope className="text-gray-600" size={20} />
                          </div>
                          <div className="min-w-0 flex-1">
                            <p className="font-medium truncate">
                              {patients.find(p => p.id === prediction.patient_id)?.first_name} {patients.find(p => p.id === prediction.patient_id)?.last_name}
                            </p>
                            <p className="text-sm text-gray-600">
                              {formatDate(prediction.created_at)}
                            </p>
                            <div className="mt-2">
                              <DualConfidenceBar confidenceScores={prediction.confidence_scores} />
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-3 sm:flex-shrink-0">
                          {getResultBadge(prediction.prediction, prediction.confidence_scores)}
                          <Button variant="ghost" size="sm">
                            <Eye size={14} />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Clock className="mx-auto text-gray-400 mb-4" size={48} />
                    <p className="text-gray-600">{t.predictions.noHistory}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
    </div>
  );
};

export default PredictionsPage;