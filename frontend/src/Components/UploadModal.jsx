import React, { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import PropTypes from 'prop-types';

// Importa os componentes UI que você criou
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Card, CardContent } from './ui/card';

// Importa os ícones
import { X, Upload, FileText, ImageIcon, Video, Music, Plus, Check, AlertCircle, Tag } from 'lucide-react'; // Certifique-se de que Trash2 está aqui!

const fileTypeIcons = {
  image: ImageIcon,
  video: Video,
  audio: Music,
  document: FileText,
};

const fileTypeColors = {
  image: 'bg-green-100 text-green-800',
  video: 'bg-blue-100 text-blue-800',
  audio: 'bg-purple-100 text-purple-800',
  // Cor da tag de documento: use uma cor sólida para não parecer opaca
  document: 'bg-gray-700 text-white', // Exemplo: cinza escuro sólido
};

const getFileType = (file) => {
  const type = file.type.split('/')[0];
  switch (type) {
    case 'image':
      return 'image';
    case 'video':
      return 'video';
    case 'audio':
      return 'audio';
    default:
      return 'document';
  }
};

export function UploadModal({ isOpen, onClose }) {
  const [uploadFile, setUploadFile] = useState(null); // Apenas um arquivo por vez
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setUploadFile({
        id: Math.random().toString(36).substr(2, 9),
        file,
        name: file.name.split('.')[0],
        description: '',
        tags: [],
        type: getFileType(file),
        progress: 0,
        status: 'pending',
        preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined,
      });
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
      'video/*': ['.mp4', '.avi', '.mov', '.wmv', '.flv'],
      'audio/*': ['.mp3', '.wav', '.flac', '.aac'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 100 * 1024 * 1024,
  });

  useEffect(() => {
    return () => {
      if (uploadFile && uploadFile.preview) {
        URL.revokeObjectURL(uploadFile.preview);
      }
    };
  }, [uploadFile]);

  const updateFile = (updates) => {
    setUploadFile((prev) => ({ ...prev, ...updates }));
  };

  const removeFile = () => {
    if (uploadFile && uploadFile.preview) {
      URL.revokeObjectURL(uploadFile.preview);
    }
    setUploadFile(null);
  };

  const addTag = (tag) => {
    if (tag.trim() && uploadFile) {
      updateFile({
        tags: [...uploadFile.tags, tag.trim()],
      });
    }
  };

  const removeTag = (tagToRemove) => {
    if (uploadFile) {
      updateFile({
        tags: uploadFile.tags.filter((tag) => tag !== tagToRemove),
      });
    }
  };

  const simulateUpload = async () => {
    if (!uploadFile) return;

    updateFile({ status: 'uploading' });
    setIsUploading(true);

    for (let progress = 0; progress <= 100; progress += 10) {
      await new Promise((resolve) => setTimeout(resolve, 200));
      updateFile({ progress });
    }

    const success = Math.random() > 0.1;
    updateFile({
      status: success ? 'completed' : 'error',
      progress: success ? 100 : 0,
    });
    setIsUploading(false);
  };

  const handleClose = () => {
    removeFile();
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className=" max-h-[90vh] max-w-screen-2xl overflow-hidden p-0">
        <DialogHeader className="p-6 pb-0">
          <DialogTitle className="text-xl font-semibold">Upload de Arquivos</DialogTitle>
          <Button
            variant="ghost"
            size="icon"
            className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground"
            onClick={handleClose}
          >
            <X className="h-4 w-4" />
            <span className="sr-only">Close</span>
          </Button>
        </DialogHeader>

        <div className="p-10 space-y-6 w-full">
          {/* Drop Zone */}
          {!uploadFile && (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
                isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-lg font-medium text-gray-900 mb-2">
                {isDragActive ? 'Solte o arquivo aqui' : 'Arraste um arquivo ou clique para selecionar'}
              </p>
              <p className="text-sm text-gray-500">
                Suporte para imagens, vídeos, áudios e documentos (máx. 100MB por arquivo)
              </p>
            </div>
          )}

          {/* File Info Card */}
          {uploadFile && (
            <div className="space-y-4 max-h-96 overflow-y-auto">
              <div className="flex items-center justify-between">
                <div className="flex gap-2">
                  <Button
                    onClick={simulateUpload}
                    disabled={isUploading || uploadFile.status !== 'pending'}
                    className="bg-black hover:bg-blue-700"
                  >
                    {isUploading ? 'Enviando...' : 'Enviar'}
                  </Button>
                  <Button variant="outline" onClick={removeFile}>
                    Remover
                  </Button>
                </div>
              </div>

              <Card className="border-gray-200 ">
                <CardContent className="p-10 w-full">
                  <div className="flex gap-x-6 items-start">
        
                    <div className="flex-shrink-0">
                      {uploadFile.preview ? (
                        <img
                          src={uploadFile.preview}
                          alt={uploadFile.name}
                          className="w-16 h-16 object-cover rounded-lg"
                        />
                      ) : (
                        <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center">
                          {React.createElement(fileTypeIcons[uploadFile.type], { className: "h-8 w-8 text-gray-400" })}
                        </div>
                      )}
                    </div>
                    <div className="flex-1 flex flex-col gap-y-3 min-w-0">
                      <div className="flex items-start justify-between "> 
                        {/* Esta div é o grupo "Badge + Tamanho" */}
                        <div className="flex items-center gap-2">
                          <Badge className={`${fileTypeColors[uploadFile.type]} px-2.5 py-0.5 rounded-full`}>
                            {/* Ícone da Badge: h-3 w-3 é mais comum e proporcional */}
                            {React.createElement(fileTypeIcons[uploadFile.type], { className: "h-3 w-3 mr-1" })}
                            {uploadFile.type}
                          </Badge>
                          <span className="text-sm text-gray-500">
                            {(uploadFile.file.size / 1024 / 1024).toFixed(2)} MB
                          </span>
                        </div>
                        {/* Div dos botões de status/lixeira */}
                        <div className="flex items-center gap-2 ">
                          {uploadFile.status === 'completed' && <Check className="h-4 w-4 text-green-600" />}
                          {uploadFile.status === 'error' && <AlertCircle className="h-4 w-4 text-red-600" />}
                         
                        </div>
                      </div>

                      {/* File Name */}
                      <Input
                        value={uploadFile.name}
                        onChange={(e) => updateFile({ name: e.target.value })}
                        placeholder="Nome do arquivo"
                        className="h-8 px-3"
                      />

                      {/* Description */}
                      <Textarea
                        value={uploadFile.description}
                        onChange={(e) => updateFile({ description: e.target.value })}
                        placeholder="Descrição (opcional)"
                        className="min-h-[60px] resize-none"
                      />

                      {/* Tags */}
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <Tag className="h-4 w-4 text-gray-500" />
                          <span className="text-sm font-medium text-gray-700">Tags</span>
                        </div>
                        <div className="flex flex-wrap gap-2 mb-2">
                          {uploadFile.tags.map((tag, index) => (
                            <Badge key={index} variant="secondary" className="text-xs">
                              {tag}
                              <button
                                onClick={() => removeTag(tag)}
                                className="ml-1 hover:bg-gray-300 rounded-full p-0.5"
                              >
                                <X className="h-2 w-2" />
                              </button>
                            </Badge>
                          ))}
                        </div>
                        <div className="flex gap-2">
                          <Input
                            placeholder="Nova tag..."
                            className="text-sm h-8 flex-1"
                            onKeyPress={(e) => {
                              if (e.key === 'Enter') {
                                addTag(e.currentTarget.value);
                                e.currentTarget.value = '';
                              }
                            }}
                          />
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={(e) => {
                              const input = e.currentTarget.parentElement?.querySelector('input');
                              if (input?.value) {
                                addTag(input.value);
                                input.value = '';
                              }
                            }}
                          >
                            <Plus className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>

                      {/* Progress Bar */}
                      {uploadFile.status === 'uploading' && (
                        <div className="space-y-1">
                          <div className="flex justify-between text-sm">
                            <span>Enviando...</span>
                            <span>{uploadFile.progress}%</span>
                          </div>
                          <Progress value={uploadFile.progress} className="h-2" />
                        </div>
                      )}

                      {uploadFile.status === 'error' && (
                        <div className="text-sm text-red-600 flex items-center gap-2">
                          <AlertCircle className="h-4 w-4" />
                          Erro no upload. Tente novamente.
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

UploadModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
};