<template>
  <nav class="navbar navbar-expand-lg bg-white border-bottom border-body" data-bs-theme="light">
    <div class="container-fluid d-flex justify-content-between align-items-center">
      <div class="d-flex align-items-center">
        <a class="navbar-brand" href="#">
          <img src="../assets/logo/Mad2_logo.png" class="logo" alt="Logo">
        </a>
        <router-link :to="{ name: 'LibrarianHome' }" v-if="loggedIn && role === 'LIBRARIAN'">
          <i class="fa-solid fa-house px-3 py-2 my-2 profile-link"></i>
        </router-link>
        <router-link :to="{ name: 'ReaderHome' }" v-if="loggedIn && role === 'READER'">
          <i class="fa-solid fa-house px-3 py-2 my-2 profile-link"></i>
        </router-link>
      </div>
      <div class="d-flex justify-content-center search">
        <form class="d-flex" @submit.prevent="search">
          <div class="input-group position-relative">
            <input v-model="searchQuery" class="form-control me-2" type="search" placeholder="Search" aria-label="Search">
            <button class="btn btn-outline-dark custom-btn" type="submit">Search</button>
          </div>
        </form>
      </div>
      <div class="profile d-flex">
        <div class="librarian mx-4" v-if="role === 'LIBRARIAN'">
          <router-link :to="{ name: 'RequestList' }" v-if="loggedIn">
            <i class="fa-regular fa-comment-dots px-3 py-2 profile-link"></i>
          </router-link>
        </div>
        <router-link :to="{ name: 'ReaderWishlist', params: { userId: userId } }" v-if="loggedIn && role === 'READER'">
          <i class="fa-solid fa-clipboard-list px-3 py-2 profile-link"></i>
        </router-link>
        <router-link :to="{ name: 'UserProfile', params: { userId: userId } }" v-if="loggedIn">
          <i class="fa-regular fa-user mx-4 px-2 py-2 profile-link"></i>
        </router-link>
        <button v-if="loggedIn" @click="logout" class="btn btn-danger">Logout</button>
        <router-link v-else to="/login" class="btn btn-success">Login</router-link>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  data() {
    return {
      searchQuery: "",
      loggedIn: false,
      userId: null,
      role: "",
    };
  },
  mounted() {
    this.checkAuthentication();
  },
  methods: {
    search() {
      if (this.searchQuery.trim() !== "") {
        this.$router.push({ name: 'searchResult', params: { query: this.searchQuery } });
      }
    },
    async logout() {
      sessionStorage.removeItem('token');
      this.$router.push('/login');
      await this.checkAuthentication();
    },
    async checkAuthentication() {
      const token = sessionStorage.getItem('token');
      if (token) {
        try {
          const response = await fetch('http://127.0.0.1:5000/verify', {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          const data = await response.json();

          if (data.authenticated) {
            this.loggedIn = true;
            this.userId = data.user.id;
            this.role = data.user.role;
          } else {
            this.loggedIn = false;
          }
        } catch (error) {
          console.error('Error verifying authentication:', error);
        }
      } else {
        this.loggedIn = false;
      }
    },
  },
};
</script>

<style scoped>
nav {
  z-index: 2;
  position: sticky;
  top: 0;
  background-color: #ffffff; 
  color: #000000; 
}

.logo {
  height: 60px;
}

.custom-btn {
  font-size: 0.8rem;
  padding: 0.25rem 0.5rem;
  width: 100px;
}

.search {
  flex: 1;
}

.profile {
  align-items: center;
}

.profile-link {
  font-size: x-large;
  color: #000000; 
}

.navbar-brand img {
  height: 60px;
}

.btn-outline-dark.custom-btn {
  color: #000000; 
  border-color: #000000;
}

.btn-outline-dark.custom-btn:hover {
  background-color: #000000; 
  color: #ffffff; 
}

.profile .btn-danger, .profile .btn-success {
  margin-left: 10px;
}
</style>
