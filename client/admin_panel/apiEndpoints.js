export const API = Object.freeze({
    USERS: {
        ME: '/api/users/me/',
        LIST: '/api/admin/users/',
        DELETE: (userId) => `/api/admin/users/${userId}/`
    },
    POSTS: {
        LIST: '/api/admin/posts/',
        DELETE: (slug) => `/api/admin/posts/${slug}/`
    }
});