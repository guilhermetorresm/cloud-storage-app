import { refreshAccessToken } from "./authUtils";

export async function fetchWithAuth(url, options = {}, navigate) {
  try {
    const token = localStorage.getItem("access_token");

    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.status === 401) {
      const refreshSuccess = await refreshAccessToken();
      if (refreshSuccess) {
        const newToken = localStorage.getItem("access_token");
        return fetch(url, {
          ...options,
          headers: {
            ...options.headers,
            Authorization: `Bearer ${newToken}`,
          },
        });
      } else {
        if (navigate) {
          navigate("/");
        }
        throw new Error("Token expirado e não foi possível renovar.");
      }
    }

    return response;
  } catch (err) {
    console.error("Erro no fetchWithAuth:", err);
    throw err;
  }
}
