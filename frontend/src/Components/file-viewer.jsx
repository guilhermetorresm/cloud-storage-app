"use client";

import { useEffect, useRef, useState } from "react";
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

const fileTypeIcons = {
  image: ImageIcon,
  video: Video,
  audio: Music,
};

const fileTypeColors = {
  image: "bg-green-500 text-green-800",
  video: "bg-blue-500 text-blue-800",
  audio: "bg-purple-500 text-purple-800",
};

export function FileViewer({ fileId, onClose }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isEditing, setIsEditing] = useState(false);
  const [editedFile, setEditedFile] = useState({
    title: "",
    description: "",
    tags: [],
    genre: "",
  });
  const [newTag, setNewTag] = useState("");

  const videoRef = useRef(null);
  const audioRef = useRef(null);

  // Função para obter o access token (você precisa implementar isso de acordo com seu app)
  const getAccessToken = () => {
    // Placeholder: Em um aplicativo real, você buscaria isso do localStorage,
    // de um contexto global ou de um hook de autenticação.
    return localStorage.getItem("access_token");
  };

  useEffect(() => {
    const fetchFile = async () => {
      setLoading(true);
      try {
        const accessToken = getAccessToken();
        if (!accessToken) {
          throw new Error("Token de acesso não encontrado. Por favor, faça login.");
        }

        const res = await fetch(`/api/v1/files/${fileId}`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });

        // Verifica se o tipo de conteúdo é JSON antes de tentar fazer o parse
        const contentType = res.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
          const errorText = await res.text();
          throw new Error(
            `Resposta inesperada do servidor: ${res.status} ${res.statusText}. Conteúdo recebido: ${errorText.substring(0, 200)}...`
          );
        }

        if (!res.ok) {
          const errorData = await res.json(); // Tenta fazer o parse como JSON se esperávamos JSON
          throw new Error(
            `Erro ao buscar arquivo: ${res.status} ${res.statusText} - ${errorData.message || 'Erro desconhecido.'}`
          );
        }

        const data = await res.json();
        setFile(data);
        setEditedFile({
          title: data.title || "",
          description: data.description || "",
          tags: data.tags || [],
          genre: data.genre || "",
        });
      } catch (err) {
        console.error("Erro ao buscar arquivo:", err);
        alert(`Não foi possível carregar o arquivo: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };
    fetchFile();
  }, [fileId]);

  if (loading) {
    return (
      <Dialog open={true} onOpenChange={onClose}>
        <DialogContent className="p-6 text-center">Carregando...</DialogContent>
      </Dialog>
    );
  }

  if (!file) {
    return (
      <Dialog open={true} onOpenChange={onClose}>
        <DialogContent className="p-6 text-center text-red-500">
          Arquivo não encontrado
        </DialogContent>
      </Dialog>
    );
  }

  const IconComponent = fileTypeIcons[file.type];

  const handleSave = async () => {
    try {
      const accessToken = getAccessToken();
      if (!accessToken) {
        throw new Error("Token de acesso não encontrado. Por favor, faça login.");
      }

      const payload = {
        new_name: editedFile.title,
        new_description: editedFile.description,
        new_tags: editedFile.tags.join(","),
        // Inclui o gênero no payload se aplicável
        ...(file.type === "audio" || file.type === "video"
          ? { new_genre: editedFile.genre }
          : {}),
      };

      const res = await fetch(`/api/v1/files/${fileId}/metadata`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify(payload),
      });

      // Verifica se o tipo de conteúdo é JSON antes de tentar fazer o parse
      const contentType = res.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        const errorText = await res.text();
        throw new Error(
          `Resposta inesperada do servidor ao salvar metadados: ${res.status} ${res.statusText}. Conteúdo recebido: ${errorText.substring(0, 200)}...`
        );
      }

      if (!res.ok) {
        const errorData = await res.json(); // Tenta fazer o parse como JSON
        throw new Error(
          `Erro ao atualizar metadados: ${res.status} ${res.statusText} - ${errorData.message || 'Erro desconhecido.'}`
        );
      }
      const updated = await res.json();

      setFile((prev) => ({
        ...prev,
        title: updated.title || payload.new_name,
        description: updated.description || payload.new_description,
        tags: updated.tags || payload.new_tags.split(","),
        genre: updated.genre || editedFile.genre,
      }));
      setEditedFile((prev) => ({
        ...prev,
        title: updated.title || prev.title,
        description: updated.description || prev.description,
        tags: updated.tags || prev.tags,
        genre: updated.genre || prev.genre,
      }));

      setIsEditing(false);
    } catch (err) {
      console.error("Erro ao salvar metadados:", err);
      alert(`Falha ao salvar alterações: ${err.message}`);
    }
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

  const removeTag = (tag) => {
    setEditedFile((prev) => ({
      ...prev,
      tags: prev.tags.filter((t) => t !== tag),
    }));
  };

  const togglePlayPause = () => {
    if (file.type === "video" && videoRef.current) {
      isPlaying ? videoRef.current.pause() : videoRef.current.play();
    } else if (file.type === "audio" && audioRef.current) {
      isPlaying ? audioRef.current.pause() : audioRef.current.play();
    }
    setIsPlaying((p) => !p);
  };

  const formatTime = (time) => {
    const min = Math.floor(time / 60);
    const sec = Math.floor(time % 60)
      .toString()
      .padStart(2, "0");
    return `${min}:${sec}`;
  };

  const getMetadataFields = () => {
    const base = [
      { icon: HardDrive, label: "Tamanho", value: file.size },
      {
        icon: Calendar,
        label: "Upload",
        value: new Date(file.uploadDate).toLocaleDateString("pt-BR"),
      },
    ];
    const extras = {
      image: [
        { icon: Monitor, label: "Dimensões", value: file.dimensions || "—" },
        { icon: Monitor, label: "Resolução", value: file.resolution || "—" },
        { icon: FileType, label: "Formato", value: file.format || "—" },
      ],
      video: [
        { icon: Monitor, label: "Dimensões", value: file.dimensions || "—" },
        { icon: Clock, label: "Duração", value: file.duration ? formatTime(file.duration) : "—" },
        { icon: FileType, label: "Formato", value: file.format || "—" },
        { icon: Tag, label: "Gênero", value: file.genre || "Não informado" },
      ],
      audio: [
        { icon: Clock, label: "Duração", value: file.duration ? formatTime(file.duration) : "—" },
        { icon: Music, label: "Bitrate", value: file.bitrate || "—" },
        { icon: Music, label: "Sample Rate", value: file.sampleRate || "—" },
        { icon: FileType, label: "Formato", value: file.format || "—" },
        { icon: Tag, label: "Gênero", value: file.genre || "Não informado" },
      ],
    };
    return [...base, ...(extras[file.type] || [])];
  };

  const renderMedia = () => {
    switch (file.type) {
      case "image":
        return (
          <div className="relative bg-gray-50 rounded-xl overflow-hidden h-full flex justify-center items-center">
            <img
              src={file.url}
              alt={file.title}
              className="max-w-full max-h-full object-contain"
            />
            <Button
              variant="secondary"
              size="icon"
              className="absolute top-4 right-4 bg-black/20 text-white"
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
              controls
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
              onLoadedMetadata={(e) => setDuration(e.currentTarget.duration)}
            />
          </div>
        );
      case "audio":
        return (
          <div className="bg-gradient-to-br from-purple-100 to-blue-100 rounded-xl p-8 h-full flex flex-col justify-center">
            <div className="text-center mb-6">
              <div className="w-24 h-24 bg-white rounded-full mx-auto mb-4 flex items-center justify-center shadow-lg">
                <Music className="h-12 w-12 text-purple-600" />
              </div>
              <h3 className="text-xl font-bold">{file.title}</h3>
            </div>
            <audio
              ref={audioRef}
              src={file.url}
              className="hidden"
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
              onLoadedMetadata={(e) => setDuration(e.currentTarget.duration)}
            />
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center gap-4">
                <Button
                  onClick={togglePlayPause}
                  className="rounded-full w-12 h-12 bg-purple-600 text-white"
                >
                  {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
                </Button>
                <div className="flex-1">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>{formatTime(currentTime)}</span>
                    <span>{formatTime(duration)}</span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-purple-600 h-2 rounded-full transition-all"
                      style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
                    />
                  </div>
                </div>
                <Button variant="ghost" size="icon" className="text-gray-600">
                  <Volume2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-screen-2xl p-6 max-h-screen overflow-hidden">
        <div className="flex justify-between items-center border-b pb-4">
          <div className="flex items-center gap-3">
            <Badge className={`${fileTypeColors[file.type]} text-xs font-medium`}>
              <IconComponent className="h-3 w-3 mr-1" />
              {file.type}
            </Badge>
            <div>
              {isEditing ? (
                <Input
                  value={editedFile.title}
                  onChange={(e) => setEditedFile((p) => ({ ...p, title: e.target.value }))}
                  className="text-xl font-semibold h-8 border-0 p-0 focus:ring"
                />
              ) : (
                <h2 className="text-xl font-semibold">{file.title}</h2>
              )}
              <p className="text-sm text-gray-600">{file.description || "Sem descrição"}</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X className="h-5 w-5" />
          </Button>
        </div>

        <div className="flex h-[calc(95vh-140px)] mt-4">
          <div className="flex-[3] p-4">{renderMedia()}</div>
          <div className="flex-1 border-l p-4 overflow-auto">
            <div className="flex justify-between mb-4">
              <h3 className="text-lg font-semibold">Informações do Arquivo</h3>
              <div>
                {isEditing ? (
                  <>
                    <Button size="sm" className="bg-green-600 hover:bg-green-700 mr-2" onClick={handleSave}>
                      <Save className="h-4 w-4 mr-1" />
                      Salvar
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setIsEditing(false)}>
                      Cancelar
                    </Button>
                  </>
                ) : (
                  <Button size="sm" variant="outline" onClick={() => setIsEditing(true)}>
                    <Edit3 className="h-4 w-4 mr-1" />
                    Editar
                  </Button>
                )}
              </div>
            </div>

            {(file.type === "audio" || file.type === "video") && (
              <div className="mb-4">
                <label className="text-sm font-medium block mb-1">Gênero</label>
                {isEditing ? (
                  <Input
                    value={editedFile.genre}
                    onChange={(e) => setEditedFile((p) => ({ ...p, genre: e.target.value }))}
                    placeholder="Ex: Música, Documentário..."
                    className="h-8"
                  />
                ) : (
                  <p className="text-sm text-gray-600">{file.genre || "Não informado"}</p>
                )}
              </div>
            )}

            <div className="mb-4">
              <label className="text-sm font-medium block mb-1">Descrição</label>
              {isEditing ? (
                <Textarea
                  value={editedFile.description}
                  onChange={(e) => setEditedFile((p) => ({ ...p, description: e.target.value }))}
                  className="h-20"
                />
              ) : (
                <p className="text-sm text-gray-600">{file.description || "Sem descrição"}</p>
              )}
            </div>

            <div className="mb-6">
              <div className="flex items-center gap-2 mb-2">
                <Tag className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium">Tags</span>
              </div>
              <div className="flex flex-wrap gap-2 mb-2">
                {editedFile.tags.map((tag, i) => (
                  <Badge key={i} variant="secondary" className="text-xs flex items-center">
                    {tag}
                    {isEditing && (
                      <button className="ml-1 text-red-500" onClick={() => removeTag(tag)}>
                        <X className="h-3 w-3" />
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
                    onKeyDown={(e) => e.key === "Enter" && addTag()}
                    className="h-8 text-sm"
                  />
                  <Button size="sm" onClick={addTag} disabled={!newTag.trim()}>
                    Adicionar
                  </Button>
                </div>
              )}
            </div>

            <Separator className="mb-4" />

            <div className="flex gap-2 mb-6">
              <Button className="flex-1 bg-blue-600 hover:bg-blue-700">
                <Download className="h-4 w-4 mr-1" />
                Download
              </Button>
              <Button variant="destructive" className="flex-1">
                <Trash2 className="h-4 w-4 mr-1" />
                Deletar
              </Button>
            </div>

            <Separator className="mb-4" />

            <div>
              <h4 className="text-sm font-medium mb-3">Metadados</h4>
              <div className="space-y-2">
                {getMetadataFields().map((f, idx) => (
                  <Card key={idx} className="border-gray-200">
                    <CardContent className="p-3 flex items-center gap-3">
                      <f.icon className="h-4 w-4 text-gray-500" />
                      <div>
                        <p className="text-xs text-gray-500">{f.label}</p>
                        <p className="text-sm font-semibold">{f.value}</p>
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