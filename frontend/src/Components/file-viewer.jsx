// Components/file-viewer.jsx
"use client";

import { useEffect, useRef, useState } from "react";
// Verifique novamente os caminhos dos seus componentes de UI
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { Dialog, DialogContent } from "./ui/dialog";
import { Separator } from "./ui/separator";

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
  pdf: FileType,
  document: FileType,
  text: FileType,
  zip: FileType,
  other: FileType,
};

const fileTypeColors = {
  image: "bg-green-500 text-green-800",
  video: "bg-blue-500 text-blue-800",
  audio: "bg-purple-500 text-purple-800",
  pdf: "bg-red-500 text-red-800",
  document: "bg-yellow-500 text-yellow-800",
  text: "bg-yellow-500 text-yellow-800",
  zip: "bg-gray-500 text-gray-800",
  other: "bg-gray-500 text-gray-800",
};

// --- AGORA: FileViewer recebe fileId, não o objeto 'file' completo ---
export function FileViewer({ fileId, onClose, onMetadataUpdate, onFileDelete }) {
  const [file, setFile] = useState(null); // Estado para o arquivo completo (detalhes da API)
  const [loading, setLoading] = useState(true); // Indica se está carregando os detalhes
  const [error, setError] = useState(null); // Erros ao carregar detalhes
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

  const getAccessToken = () => {
    return localStorage.getItem("access_token");
  };

  // --- useEffect para buscar os detalhes do arquivo ---
  useEffect(() => {
    if (!fileId) {
      setLoading(false);
      setError("Nenhum ID de arquivo fornecido.");
      return;
    }

    const fetchFileDetails = async () => {
      setLoading(true);
      setError(null);
      try {
        const accessToken = getAccessToken();
        if (!accessToken) {
          throw new Error("Token de acesso não encontrado. Por favor, faça login.");
        }

        // Requisição para a API de detalhes do arquivo
        const response = await fetch(
          `${process.env.REACT_APP_API_URL}/api/v1/files/${fileId}`,
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          }
        );

        if (!response.ok) {
          const contentType = response.headers.get("content-type");
          if (contentType && contentType.includes("application/json")) {
            const errorData = await response.json();
            throw new Error(errorData.message || `Erro ao buscar detalhes: ${response.status}`);
          } else {
            const errorText = await response.text();
            throw new Error(`Resposta inesperada do servidor ao buscar detalhes: ${response.status}. Conteúdo: ${errorText.substring(0, 200)}...`);
          }
        }

        const data = await response.json();
        // Console.log para depuração: veja o que vem da API de detalhes
        console.log("Dados detalhados do arquivo:", data);

        // Mapear os dados da API para o formato esperado no frontend
        const fileData = {
            id: data.metadata.file_id,
            title: data.metadata.name,
            description: data.metadata.description || "",
            type: data.metadata.category, // 'category' é o tipo (image, video, etc.)
            url: data.download_url, // <<< A URL PRINCIPAL PARA DOWNLOAD/VISUALIZAÇÃO ESTÁ AQUI >>>
            thumbnail_url: data.metadata.thumbnail_url || null, // A URL da thumbnail
            size: data.metadata.size, // Tamanho em bytes
            size_humanized: data.metadata.size_humanized, // Tamanho formatado
            uploadDate: new Date(data.metadata.created_at).toLocaleDateString("pt-BR"),
            // Campos específicos de mídia/documento:
            dimensions: data.metadata.dimensions || null, // Ex: "453x640"
            resolution: data.metadata.dpi ? `${data.metadata.dpi} DPI` : null, // Ex: "96 DPI"
            format: data.metadata.extension || data.metadata.mime_type || null, // Ex: "png", "image/png"
            genre: data.metadata.genre || "", // Para áudio/vídeo
            duration: data.metadata.duration_humanized || null, // Para áudio/vídeo
            bitrate: data.metadata.bitrate_humanized || null, // Para áudio/vídeo
            sampleRate: data.metadata.sample_rate_humanized || null, // Para áudio
            pages: data.metadata.pages || null, // Para PDFs
            tags: Array.isArray(data.metadata.tags) ? data.metadata.tags : (data.metadata.tags ? String(data.metadata.tags).split(',').map(tag => tag.trim()) : []),
        };

        setFile(fileData);
        setEditedFile({
          title: fileData.title,
          description: fileData.description,
          tags: fileData.tags,
          genre: fileData.genre,
        });

      } catch (err) {
        console.error("Erro ao buscar detalhes do arquivo:", err);
        setError(`Não foi possível carregar os detalhes do arquivo: ${err.message}`);
        setFile(null);
      } finally {
        setLoading(false);
      }
    };
    fetchFileDetails();
  }, [fileId]); // Re-executa quando o fileId muda

  if (loading) {
    return (
      <Dialog open={true} onOpenChange={onClose}>
        <DialogContent className="p-6 text-center">Carregando detalhes do arquivo...</DialogContent>
      </Dialog>
    );
  }

  if (error) {
    return (
      <Dialog open={true} onOpenChange={onClose}>
        <DialogContent className="p-6 text-center text-red-500">
          Erro: {error}
          <Button onClick={onClose} className="mt-4">Fechar</Button>
        </DialogContent>
      </Dialog>
    );
  }

  if (!file) {
    return (
      <Dialog open={true} onOpenChange={onClose}>
        <DialogContent className="p-6 text-center text-red-500">
          Arquivo não encontrado ou erro inesperado.
          <Button onClick={onClose} className="mt-4">Fechar</Button>
        </DialogContent>
      </Dialog>
    );
  }

  // Agora 'file' contém todos os metadados detalhados
  const fileToDisplay = file;
  const IconComponent = fileTypeIcons[fileToDisplay.type] || fileTypeIcons.other;

  // APROXIMADAMENTE A PARTIR DAQUI (linha 316, dependendo de como você formatou o código)
const handleDelete = async () => {
    if (!fileToDisplay || !fileToDisplay.id) {
      alert("ID do arquivo não disponível para exclusão.");
      return;
    }

    if (!window.confirm(`Tem certeza que deseja deletar o arquivo "${fileToDisplay.title}"? Esta ação é irreversível.`)) {
      return;
    }

    try {
      const accessToken = getAccessToken();
      if (!accessToken) {
        throw new Error("Token de acesso não encontrado. Por favor, faça login.");
      }

      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/api/v1/files/${fileToDisplay.id}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      if (!response.ok) {
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
          const errorData = await response.json();
          throw new Error(errorData.message || `Erro ao deletar: ${response.status}`);
        } else {
          const errorText = await response.text();
          throw new Error(`Resposta inesperada do servidor ao deletar: ${response.status}. Conteúdo: ${errorText.substring(0, 200)}...`);
        }
      }

      alert("Arquivo deletado com sucesso!");
      onClose();
      if (onFileDelete) {
        onFileDelete(fileToDisplay.id);
      }
    } catch (err) {
      console.error("Erro ao deletar arquivo:", err);
      alert(`Falha ao deletar arquivo: ${err.message}`);
    }
};

  const handleSave = async () => {
    try {
      const accessToken = getAccessToken();
      if (!accessToken) {
        throw new Error("Token de acesso não encontrado. Por favor, faça login.");
      }

      const tagsString = Array.isArray(editedFile.tags) ? editedFile.tags.join(",") : "";

      const payload = {
        name: editedFile.title, // 'name' para o backend
        description: editedFile.description,
        tags: tagsString,
        ...(fileToDisplay.type === "audio" || fileToDisplay.type === "video"
          ? { genre: editedFile.genre }
          : {}),
      };

      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/api/v1/files/${fileToDisplay.id}/metadata`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: "Erro desconhecido." }));
        throw new Error(errorData.message || `Erro ao salvar: ${response.status}`);
      }

      const updatedData = await response.json();
      console.log("Resposta do PATCH:", updatedData); // Veja o que o PATCH retorna

      // Atualiza o estado local do FileViewer com os dados do PATCH ou editados
      setFile((prevFile) => ({
        ...prevFile,
        title: updatedData.metadata?.name || editedFile.title, // Acessa updatedData.metadata.name
        description: updatedData.metadata?.description || editedFile.description,
        tags: Array.isArray(updatedData.metadata?.tags) ? updatedData.metadata.tags : (updatedData.metadata?.tags ? String(updatedData.metadata.tags).split(',').map(tag => tag.trim()) : []),
        genre: updatedData.metadata?.genre || editedFile.genre,
        // Se o PATCH retorna a download_url completa de novo, pode atualizar também
        url: updatedData.download_url || prevFile.url
      }));

      setEditedFile({
        title: updatedData.metadata?.name || editedFile.title,
        description: updatedData.metadata?.description || editedFile.description,
        tags: Array.isArray(updatedData.metadata?.tags) ? updatedData.metadata.tags : (updatedData.metadata?.tags ? String(updatedData.metadata.tags).split(',').map(tag => tag.trim()) : []),
        genre: updatedData.metadata?.genre || editedFile.genre,
      });

      if (onMetadataUpdate) {
        // Envia APENAS as informações que a Dashboard precisa atualizar na lista.
        // A Dashboard não precisa de "dimensions", "resolution" para sua lista simples.
        onMetadataUpdate(fileToDisplay.id, {
          title: updatedData.metadata?.name || editedFile.title,
          description: updatedData.metadata?.description || editedFile.description,
          tags: Array.isArray(updatedData.metadata?.tags) ? updatedData.metadata.tags : (updatedData.metadata?.tags ? String(updatedData.metadata.tags).split(',').map(tag => tag.trim()) : []),
          genre: updatedData.metadata?.genre || editedFile.genre,
          // Se sua Dashboard precisa da thumbnail_url ou url atualizada, inclua aqui.
          thumbnail_url: updatedData.metadata?.thumbnail_url || fileToDisplay.thumbnail_url,
          url: updatedData.download_url || fileToDisplay.url // Se a url de download pode mudar
        });
      }

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
    if (fileToDisplay.type === "video" && videoRef.current) {
      isPlaying ? videoRef.current.pause() : videoRef.current.play();
    } else if (fileToDisplay.type === "audio" && audioRef.current) {
      isPlaying ? audioRef.current.pause() : audioRef.current.play();
    }
    setIsPlaying((p) => !p);
  };

  const formatTime = (time) => {
    if (isNaN(time) || time < 0 || time === undefined || time === null) return "0:00";
    // Tenta converter para número se for string
    const numTime = typeof time === 'string' ? parseFloat(time) : time;
    const min = Math.floor(numTime / 60);
    const sec = Math.floor(numTime % 60).toString().padStart(2, "0");
    return `${min}:${sec}`;
  };

  const getMetadataFields = () => {
    const base = [
      { icon: HardDrive, label: "Tamanho", value: fileToDisplay.size_humanized || "—" },
      {
        icon: Calendar,
        label: "Upload",
        value: fileToDisplay.uploadDate || "—",
      },
    ];
    const extras = {
      image: [
        { icon: Monitor, label: "Dimensões", value: fileToDisplay.dimensions || "—" },
        { icon: Monitor, label: "Resolução", value: fileToDisplay.resolution || (fileToDisplay.dpi ? `${fileToDisplay.dpi} DPI` : "—") }, // Usa DPI se resolution não vier formatada
        { icon: FileType, label: "Formato", value: fileToDisplay.format || "—" },
        // Adicionar outros metadados de imagem se quiser:
        // { icon: Monitor, label: "Largura", value: fileToDisplay.width || "—" },
        // { icon: Monitor, label: "Altura", value: fileToDisplay.height || "—" },
        // { icon: Tag, label: "Profundidade de Cor", value: fileToDisplay.color_depth || "—" },
        // { icon: Tag, label: "Compressão", value: fileToDisplay.compression || "—" },
        // { icon: Camera, label: "Câmera", value: fileToDisplay.camera_make && fileToDisplay.camera_model ? `${fileToDisplay.camera_make} ${fileToDisplay.camera_model}` : "—" },
      ],
      video: [
        { icon: Monitor, label: "Dimensões", value: fileToDisplay.dimensions || "—" },
        { icon: Clock, label: "Duração", value: fileToDisplay.duration || "—" }, // Já deve vir formatado
        { icon: FileType, label: "Formato", value: fileToDisplay.format || "—" },
        { icon: Tag, label: "Gênero", value: fileToDisplay.genre || "Não informado" },
        { icon: Music, label: "Bitrate", value: fileToDisplay.bitrate || "—" },
      ],
      audio: [
        { icon: Clock, label: "Duração", value: fileToDisplay.duration || "—" }, // Já deve vir formatado
        { icon: Music, label: "Bitrate", value: fileToDisplay.bitrate || "—" },
        { icon: Music, label: "Sample Rate", value: fileToDisplay.sampleRate || "—" },
        { icon: FileType, label: "Formato", value: fileToDisplay.format || "—" },
        { icon: Tag, label: "Gênero", value: fileToDisplay.genre || "Não informado" },
      ],
      pdf: [
        { icon: FileType, label: "Formato", value: fileToDisplay.format || "PDF" },
        { icon: Monitor, label: "Páginas", value: fileToDisplay.pages || "—" },
        { icon: Monitor, label: "Dimensões", value: fileToDisplay.dimensions || "—" }, // PDFs também podem ter dimensões
      ],
      document: [
        { icon: FileType, label: "Formato", value: fileToDisplay.format || "Documento" },
      ],
      text: [
        { icon: FileType, label: "Formato", value: fileToDisplay.format || "Texto" },
      ],
      zip: [
        { icon: FileType, label: "Formato", value: fileToDisplay.format || "ZIP" },
      ],
    };
    return [...base, ...(extras[fileToDisplay.type] || [])];
  };

  const renderMedia = () => {
    // A URL principal para visualização é fileToDisplay.url
    if (!fileToDisplay.url) {
      return (
        <div className="flex flex-col items-center justify-center h-full text-gray-500">
          <p>URL do arquivo não disponível.</p>
        </div>
      );
    }

    switch (fileToDisplay.type) {
      case "image":
        return (
          <div className="relative bg-gray-50 rounded-xl overflow-hidden w-full h-full flex justify-center items-center">
            <img
              src={fileToDisplay.url} // Usa a URL principal
              alt={fileToDisplay.title || "Imagem"}
              className="max-w-full max-h-full object-contain"
            />
            <Button
              variant="secondary"
              size="icon"
              className="absolute top-4 right-4 bg-black/20 text-white"
              onClick={() => window.open(fileToDisplay.url, "_blank")}
            >
              <Maximize className="h-4 w-4" />
            </Button>
          </div>
        );
      case "video":
        return (
          <div className="relative bg-black rounded-xl overflow-hidden w-full h-full flex justify-center items-center">
            <video
              ref={videoRef}
              src={fileToDisplay.url} // Usa a URL principal para o vídeo
              poster={fileToDisplay.thumbnail_url} // Usa a thumbnail_url para o poster
              className="max-w-full max-h-full object-contain"
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
          <div className="bg-gradient-to-br from-purple-100 to-blue-100 rounded-xl p-8 w-full h-full flex flex-col justify-center items-center">
            <div className="text-center mb-6">
              <div className="w-24 h-24 bg-white rounded-full mx-auto mb-4 flex items-center justify-center shadow-lg">
                <Music className="h-12 w-12 text-purple-600" />
              </div>
              <h3 className="text-xl font-bold">{fileToDisplay.title}</h3>
            </div>
            <audio
              ref={audioRef}
              src={fileToDisplay.url} // Usa a URL principal para o áudio
              className="hidden"
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
              onLoadedMetadata={(e) => setDuration(e.currentTarget.duration)}
            />
            <div className="bg-white rounded-lg p-4 shadow-sm w-full max-w-sm">
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
                    <span>{fileToDisplay.duration || formatTime(duration)}</span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-purple-600 h-2 rounded-full transition-all"
                      style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      case "pdf":
      case "document":
      case "text":
      case "zip":
      case "other":
        return (
          <div className="flex flex-col items-center justify-center h-full text-gray-700 bg-gray-50 rounded-xl p-8">
            <IconComponent className="h-20 w-20 text-gray-400 mb-4" />
            <p className="text-lg font-semibold mb-2">{fileToDisplay.title}</p>
            <p className="text-sm text-gray-500 mb-4">Pré-visualização não disponível. Faça o download para abrir.</p>
            <a
              href={fileToDisplay.url} // URL principal para download
              download={fileToDisplay.title || "document"}
              className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background bg-blue-600 text-white hover:bg-blue-700 h-10 px-4 py-2"
            >
              <Download className="h-4 w-4 mr-2" /> Download
            </a>
          </div>
        );
      default:
        return (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <IconComponent className="h-16 w-16 mb-4" />
            <p className="text-lg">Tipo de arquivo não suportado para visualização.</p>
            <p className="text-sm">Por favor, faça o download para abrir.</p>
          </div>
        );
    }
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent
        className="w-full max-w-[1280px] h-[720px] p-0 overflow-hidden rounded-2xl shadow-2xl flex flex-col"
        style={{ minWidth: '900px', minHeight: '500px' }}
      >
        <div className="flex justify-between items-center border-b px-8 py-5">
          <div className="flex items-center gap-3">
            <Badge className={`${fileTypeColors[fileToDisplay.type] || fileTypeColors.other} text-xs font-medium`}>
              <IconComponent className="h-3 w-3 mr-1" />
              {fileToDisplay.type || "Desconhecido"}
            </Badge>
            <div>
              {isEditing ? (
                <Input
                  value={editedFile.title}
                  onChange={(e) => setEditedFile((p) => ({ ...p, title: e.target.value }))}
                  className="text-xl font-semibold h-8 border-0 p-0 focus:ring"
                />
              ) : (
                <h2 className="text-xl font-semibold">{fileToDisplay.title || "Nome do Arquivo"}</h2>
              )}
              <p className="text-sm text-gray-600">{fileToDisplay.description || "Sem descrição"}</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X className="h-5 w-5" />
          </Button>
        </div>

        <div className="flex flex-1 min-h-0">
          <div className="flex-[3] p-8 flex items-center justify-center min-h-0">
            {renderMedia()}
          </div>
          <div className="flex-1 border-l p-8 overflow-y-auto min-w-[340px]">
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

            {(fileToDisplay.type === "audio" || fileToDisplay.type === "video") && (
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
                  <p className="text-sm text-gray-600">{fileToDisplay.genre || "Não informado"}</p>
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
                <p className="text-sm text-gray-600">{fileToDisplay.description || "Sem descrição"}</p>
              )}
            </div>

            <div className="mb-6">
              <div className="flex items-center gap-2 mb-2">
                <Tag className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium">Tags</span>
              </div>
              <div className="flex flex-wrap gap-2 mb-2">
                {Array.isArray(editedFile.tags) && editedFile.tags.map((tag, i) => (
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
              <a
                href={fileToDisplay.url}
                download={fileToDisplay.title || "file"}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white rounded-md px-4 py-2 text-sm font-medium inline-flex items-center justify-center"
              >
                <Download className="h-4 w-4 mr-1" />
                Download
              </a>
              <Button variant="destructive" className="flex-1" onClick={handleDelete}>
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