import api from "./api";

export const login = async (usuario, senha) => {
    return api.post('/api/v1/auth/login', {
        username: usuario,
        password: senha
    });
};