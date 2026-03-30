import api from "./api";

export interface UploadedImage {
  id: string;
  filename: string;
  original_filename: string;
  mime_type: string;
  file_size: number;
  width: number;
  height: number;
  created_at: string;
}

export const imageService = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post<UploadedImage>("/images/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then((r) => r.data);
  },
  getImageUrl: (imageId: string) => `/api/v1/images/file/${imageId}`,
  getStepImageUrl: (jobId: string, stepNumber: number) => `/api/v1/jobs/${jobId}/steps/${stepNumber}/image`,
  delete: (imageId: string) => api.delete(`/images/${imageId}`),
};
