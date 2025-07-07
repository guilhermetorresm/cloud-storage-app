"use client";

import { useState, useRef } from "react";
// Certifique-se de que os caminhos de importação para seus componentes UI estão corretos
import { Button } from "../Components/ui/button";
import { Input } from "../Components/ui/input";
import { Textarea } from "../Components/ui/textarea";
import { Card, CardContent } from "../Components/ui/card";
import { Badge } from "../Components/ui/badge";
import { Dialog, DialogContent } from "../Components/ui/dialog";
import { Separator } from "../Components/ui/separator";
import {
  X,
  Download,
  Calendar,
  HardDrive,
  ImageIcon,
  Video,
  Music,
  FileText,
  Play,
  Pause,
  Volume2,
  Maximize,
  Trash2,
  Tag,
  Edit3,
  Save,
  Monitor,
  FileType,
  Clock,
} from "lucide-react";
// Importe Image se estiver usando Next.js Image component

// If you are using Next.js Image component, ensure it's imported:
// import Image from "next/image" // Uncomment if you use <Image /> from Next.js

// --- THESE DECLARATIONS MUST BE AT THE TOP LEVEL OF THE FILE ---
// (Outside of any function component, but after imports)

const fileTypeIcons = {
  image: ImageIcon,
  video: Video,
  audio: Music,
  document: FileText,
};

const fileTypeColors = {
  image: "bg-green-500 text-green-800",
  video: "bg-blue-500 text-blue-800",
  audio: "bg-purple-500 text-purple-800",
  document: "bg-orange-500 text-orange-800",
};

// --- End of top-level declarations ---

// You can also define interfaces here if you're using TypeScript
// interface FileItem { /* ... */ }
// interface FileViewerProps { file: FileItem; onClose: () => void; }

export function FileViewer({ file, onClose }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isEditing, setIsEditing] = useState(false);
  const [editedFile, setEditedFile] = useState({
    title: file.title,
    description: file.description || "",
    tags: file.tags || [],
    genre: file.genre || "",
  });
  const [newTag, setNewTag] = useState("");

  const videoRef = useRef(null);
  const audioRef = useRef(null);

  // This line now correctly accesses 'fileTypeIcons' because it's defined in scope
  const IconComponent = fileTypeIcons[file.type];

  const handleSave = () => {
    console.log("Saving file data:", editedFile);
    setIsEditing(false);
  };

  const addTag = () => {
    if (newTag.trim() && !editedFile.tags.includes(newTag.trim())) {
      setEditedFile((prev) => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()],
      }));
      setNewTag("");
    }
  };

  const removeTag = (tagToRemove) => {
    setEditedFile((prev) => ({
      ...prev,
      tags: prev.tags.filter((tag) => tag !== tagToRemove),
    }));
  };

  const togglePlayPause = () => {
    if (file.type === "video" && videoRef.current) {
      isPlaying ? videoRef.current.pause() : videoRef.current.play();
    } else if (file.type === "audio" && audioRef.current) {
      isPlaying ? audioRef.current.pause() : audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, "0")}`;
  };

  const renderMediaContent = () => {
    switch (file.type) {
      case "image":
        return (
          <div className="relative bg-gray-50 rounded-xl overflow-hidden h-full flex items-center justify-center">
            {/* Use <img> tag if not importing Next.js Image component */}
            <img
              src={file.url || "/placeholder.svg"}
              alt={file.title}
              className="max-w-full max-h-full object-contain"
            />
            <Button
              variant="secondary"
              size="icon"
              className="absolute top-4 right-4 bg-black/20 hover:bg-black/40 text-white border-0"
            >
              <Maximize className="h-4 w-4" />
            </Button>
          </div>
        );
      case "video":
        return (
          <div className="relative bg-black rounded-xl overflow-hidden h-full">
            <video
              ref={videoRef}
              src={file.url}
              poster={file.thumbnail}
              className="w-full h-full object-contain"
              onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
              onLoadedMetadata={(e) => setDuration(e.currentTarget.duration)}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              controls
            />
          </div>
        );
      case "audio":
        return (
          <div className="bg-gradient-to-br from-purple-100 to-blue-100 rounded-xl p-8 h-full flex flex-col justify-center">
            <div className="text-center mb-6">
              <div className="mx-auto w-24 h-24 bg-white rounded-full flex items-center justify-center mb-4 shadow-lg">
                <Music className="h-12 w-12 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900">
                {file.title}
              </h3>
            </div>
            <audio
              ref={audioRef}
              src={file.url}
              onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
              onLoadedMetadata={(e) => setDuration(e.currentTarget.duration)}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              className="hidden"
            />
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center gap-4">
                <Button
                  onClick={togglePlayPause}
                  className="bg-purple-600 hover:bg-purple-700 text-white rounded-full w-12 h-12"
                >
                  {isPlaying ? (
                    <Pause className="h-5 w-5" />
                  ) : (
                    <Play className="h-5 w-5" />
                  )}
                </Button>
                <div className="flex-1">
                  <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                    <span>{formatTime(currentTime)}</span>
                    <span>{formatTime(duration)}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-purple-600 h-2 rounded-full transition-all"
                      style={{
                        width: `${
                          duration ? (currentTime / duration) * 100 : 0
                        }%`,
                      }}
                    />
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-gray-600 hover:bg-gray-100"
                >
                  <Volume2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        );
      case "document":
        return (
          <div className="bg-gray-50 rounded-xl p-8 text-center h-full flex flex-col justify-center">
            <div className="mx-auto w-24 h-24 bg-orange-100 rounded-full flex items-center justify-center mb-4">
              <FileText className="h-12 w-12 text-orange-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {file.title}
            </h3>
            <p className="text-gray-600 mb-6">
              Documento não pode ser visualizado diretamente
            </p>
            <Button className="bg-orange-600 hover:bg-orange-700 text-white mx-auto">
              <Download className="h-4 w-4 mr-2" />
              Baixar Documento
            </Button>
          </div>
        );
      default:
        return null;
    }
  };

  const getMetadataFields = () => {
    const commonFields = [
      { icon: HardDrive, label: "Tamanho", value: file.size },
      {
        icon: Calendar,
        label: "Data de Upload",
        value: new Date(file.uploadDate).toLocaleDateString("pt-BR"),
      },
    ];
    switch (file.type) {
      case "image":
        return [
          ...commonFields,
          {
            icon: Monitor,
            label: "Dimensões",
            value: file.dimensions || "1920x1080",
          },
          {
            icon: Monitor,
            label: "Resolução",
            value: file.resolution || "72 DPI",
          },
          { icon: FileType, label: "Formato", value: file.format || "PNG" },
        ];
      case "video":
        return [
          ...commonFields,
          {
            icon: Monitor,
            label: "Dimensões",
            value: file.dimensions || "1920x1080",
          },
          { icon: Clock, label: "Duração", value: file.duration || "3:24" },
          { icon: FileType, label: "Formato", value: file.format || "MP4" },
          {
            icon: Tag,
            label: "Gênero",
            value: file.genre || "Não especificado",
          },
        ];
      case "audio":
        return [
          ...commonFields,
          { icon: Clock, label: "Duração", value: file.duration || "15:30" },
          { icon: Music, label: "Bitrate", value: file.bitrate || "320 kbps" },
          {
            icon: Music,
            label: "Sample Rate",
            value: file.sampleRate || "44.1 kHz",
          },
          { icon: FileType, label: "Formato", value: file.format || "MP3" },
          {
            icon: Tag,
            label: "Gênero",
            value: file.genre || "Não especificado",
          },
        ];
      case "document":
        return [
          ...commonFields,
          {
            icon: FileText,
            label: "Páginas",
            value: file.pages?.toString() || "12",
          },
          { icon: FileType, label: "Formato", value: file.format || "PDF" },
        ];
      default:
        return commonFields;
    }
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-screen-2xl max-h-screen overflow-hidden p-6">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            {/* This line now correctly accesses 'fileTypeColors' */}
            <Badge
              className={`${fileTypeColors[file.type]} text-xs font-medium`}
            >
              <IconComponent className="h-3 w-3 mr-1" />
              {file.type}
            </Badge>
            <div>
              {isEditing ? (
                <Input
                  value={editedFile.title}
                  onChange={(e) =>
                    setEditedFile((prev) => ({
                      ...prev,
                      title: e.target.value,
                    }))
                  }
                  className="text-xl font-semibold h-8 border-0 p-0 focus-visible:ring-1"
                />
              ) : (
                <h2 className="text-xl font-semibold text-gray-900">
                  {editedFile.title}
                </h2>
              )}
              <p className="text-sm text-gray-600 mt-1">
                {editedFile.description || "Sem descrição"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="absolute top-4 right-4 z-10 text-gray-500 hover:text-gray-700"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex h-[calc(95vh-140px)] w-full">
          {/* Left Side - File Content */}
          <div className="flex-[3] p-6">{renderMediaContent()}</div>

          {/* Right Side - File Information */}
          <div className=" flex-1 border-l border-gray-200 p-6 overflow-y-auto">
            {/* Edit Controls */}
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">
                Informações do Arquivo
              </h3>
              <div className="flex gap-2">
                {isEditing ? (
                  <>
                    <Button
                      size="sm"
                      onClick={handleSave}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <Save className="h-4 w-4 mr-1" />
                      Salvar
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setIsEditing(false)}
                    >
                      Cancelar
                    </Button>
                  </>
                ) : (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setIsEditing(true)}
                  >
                    <Edit3 className="h-4 w-4 mr-1" />
                    Editar
                  </Button>
                )}
              </div>
            </div>

            {/* Genre field for audio and video files */}
            {(file.type === "audio" || file.type === "video") && (
              <div className="mb-4">
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Gênero
                </label>
                {isEditing ? (
                  <Input
                    value={editedFile.genre}
                    onChange={(e) =>
                      setEditedFile((prev) => ({
                        ...prev,
                        genre: e.target.value,
                      }))
                    }
                    placeholder="Ex: Educacional, Música, Documentário..."
                    className="h-8"
                  />
                ) : (
                  <p className="text-sm text-gray-600 py-2">
                    {editedFile.genre || "Não especificado"}
                  </p>
                )}
              </div>
            )}

            <div className="mb-4">
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                Descrição
              </label>
              {isEditing ? (
                <Textarea
                  value={editedFile.description}
                  onChange={(e) =>
                    setEditedFile((prev) => ({
                      ...prev,
                      description: e.target.value,
                    }))
                  }
                  placeholder="Adicionar descrição..."
                  className="text-sm text-gray-600 min-h-[80px] resize-none"
                />
              ) : (
                <p className="text-sm text-gray-600 py-2">
                  {editedFile.description || "Sem descrição"}
                </p>
              )}
            </div>

            {/* Tags Section */}
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-3">
                <Tag className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">Tags</span>
              </div>

              <div className="flex flex-wrap gap-2 mb-3">
                {editedFile.tags.map((tag, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {tag}
                    {isEditing && (
                      <button
                        onClick={() => removeTag(tag)}
                        className="ml-1 hover:bg-gray-300 rounded-full p-0.5"
                      >
                        <X className="h-2 w-2" />
                      </button>
                    )}
                  </Badge>
                ))}
              </div>

              {isEditing && (
                <div className="flex gap-2">
                  <Input
                    placeholder="Nova tag..."
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && addTag()}
                    className="text-sm h-8"
                  />
                  <Button size="sm" onClick={addTag} disabled={!newTag.trim()}>
                    Adicionar
                  </Button>
                </div>
              )}
            </div>

            <Separator className="mb-6" />

            {/* Action Buttons */}
            <div className="flex gap-2 mb-6 w-full">
              <Button className="flex-1 bg-blue-600 hover:bg-blue-700">
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
              <Button variant="destructive" className="flex-1">
                <Trash2 className="h-4 w-4 mr-2" />
                Deletar
              </Button>
            </div>

            <Separator className="mb-6" />

            {/* Metadata */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-4">
                Metadados
              </h4>
              <div className="space-y-4">
                {getMetadataFields().map((field, index) => (
                  <Card key={index} className="border-gray-200">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-3">
                        <field.icon className="h-4 w-4 text-gray-500" />
                        <div className="flex-1">
                          <p className="text-xs text-gray-500 font-medium">
                            {field.label}
                          </p>
                          <p className="text-sm font-semibold text-gray-900">
                            {field.value}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
