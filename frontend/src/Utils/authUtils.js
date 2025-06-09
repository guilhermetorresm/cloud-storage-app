

export async function refreshAccessToken() {
  try {
    const refreshToken = localStorage.getItem("refresh_token");
    const response = await fetch(
      `${process.env.REACT_APP_API_URL}/api/v1/auth/refresh?refresh_token=${refreshToken}`,
      {
        method: "POST",
      }
    );

    if (!response.ok) {
      console.error("Falha ao renovar token");
      return false;
    }

    const data = await response.json();
    localStorage.setItem("access_token", data.access_token);
    return true;
  } catch (err) {
    console.error("Erro ao tentar renovar token:", err);
    return false;
  }
}
