const API_BASE = "http://localhost:8000/v1";

export const uploadFile = async (file, type) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("file_type", type);

  const response = await fetch(`${API_BASE}/files/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.message || "Failed to upload file");
  }

  const resJson = await response.json();
  return resJson.data; // UploadedFileRead
};

export const createAnalysisJob = async (jdFileId, resumeFileIds) => {
  const response = await fetch(`${API_BASE}/analysis/jobs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      job_description_file_id: jdFileId,
      resume_file_ids: resumeFileIds,
    }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.message || "Failed to create analysis job");
  }

  const resJson = await response.json();
  return resJson.data; // AnalysisJobRead
};

export const getJobStatus = async (jobId) => {
  const response = await fetch(`${API_BASE}/analysis/jobs/${jobId}`);
  if (!response.ok) {
    throw new Error("Failed to check job status");
  }
  const resJson = await response.json();
  return resJson.data; // AnalysisJobRead
};

export const getRanking = async (jobId) => {
  const response = await fetch(`${API_BASE}/analysis/jobs/${jobId}/ranking`);
  if (!response.ok) {
    throw new Error("Failed to load rankings");
  }
  const resJson = await response.json();
  return resJson.data; // RankingResultRead
};

export const getCandidateInsights = async (candidateId) => {
  const response = await fetch(`${API_BASE}/candidates/${candidateId}/insights`);
  if (!response.ok) {
    throw new Error("Failed to load candidate insights");
  }
  const resJson = await response.json();
  return resJson.data; // HiringRecommendationRead
};

export const getJobAnalytics = async (jobId) => {
  const response = await fetch(`${API_BASE}/analysis/jobs/${jobId}/analytics`);
  if (!response.ok) {
    throw new Error("Failed to load sourcing analytics");
  }
  const resJson = await response.json();
  return resJson.data; // JobAnalyticsResponse
};

export const getJobExecutiveSummary = async (jobId) => {
  const response = await fetch(`${API_BASE}/analysis/jobs/${jobId}/executive-summary`);
  if (!response.ok) {
    throw new Error("Failed to load executive summary");
  }
  const resJson = await response.json();
  return resJson.data; // JobExecutiveSummaryResponse
};
