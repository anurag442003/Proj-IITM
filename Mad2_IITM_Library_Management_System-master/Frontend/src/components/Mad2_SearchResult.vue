<template>
  <div class="custom-container">
    <section class="single-container">
      <div v-if="searchResults && searchResults.length > 0">
        <h3 class="mb-4">Professional Results</h3>
        <div class="slider-professional">
          <component 
            :is="userRole === 'ADMIN' ? 'admin-professional-card' : 'professional-card'" 
            v-for="(result, index) in searchResults" 
            :key="index" 
            :professional="result"
            :decodedImage="getDecodedImage(result)"
            v-bind="getComponentProps(result)"
            @professional-updated="updatedProfessional">
          </component>
        </div>
      </div>
      <div v-else class="center">
        <h2>NO MATCH FOUND</h2>
      </div>
    </section>
  </div>
</template>

<script>
import ProfessionalCard from './Mad2_ProfessionalCard.vue'
import AdminProfessionalCard from './Mad2_AdminProfessionalCard.vue'
export default {
  components: {
    ProfessionalCard,
    AdminProfessionalCard,
  },
  data() {
    return {
      searchResults: null,
      userRole: null,
      results: [],
    };
  },
  async created() {
    const token = sessionStorage.getItem('token');
    const user = this.$jwtDecode(token);
    const userRole = user.role;
    if (userRole === 'LIBRARIAN') {
      this.isLibrarian = true;
    }
    await this.fetchSearchResults();
  },
  watch: {
    '$route'(to, from) { // eslint-disable-line no-unused-vars
      this.fetchSearchResults();
    }
  },
  methods: {
    updatedProfessional() {
      this.fetchSearchResults()
    },
    async fetchSearchResults() {
      const query = this.$route.params.query;
      try {
        let headers = {};
        const token = sessionStorage.getItem('token');
        if (token) {
          headers = {
            Authorization: `Bearer ${token}`
          };
        }

        const apiUrl = `http://127.0.0.1:5000/search-result?query=${query}`;
        const response = await fetch(apiUrl, { headers });

        if (!response.ok) {
          throw new Error(`Failed to fetch search results: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        this.searchResults = data.results;
        this.userRole = data.userRole;
      } catch (error) {
        console.error("Error fetching search results:", error);
      }
    },
    getComponentProps(result) {
      // Return different props based on user role
      if (this.userRole === 'ADMIN') {
        return {
          uploadedBy: result.uploaded_by,
          publishYear: result.date_of_birth,
          price: result.price,
          noOfYears: result.no_of_years,
          isVerified: result.is_verified
        };
      }
      return {
        isIssued: result.isIssued,
        isRequested: result.isRequested,
        isRead: result.isRead
      };
    },
    getDecodedImage(professional) {
      const decodedImage = `data:image/${professional.imageType};base64, ${professional.image}`;
      return decodedImage;
    }
  }
};
</script>

<style scoped>
.custom-container {
  display: flex;
  flex-direction: column;
  row-gap: 2rem;
  align-items: center;
  padding-top: 2rem;
}

.single-container {
  color: white;
  background-color: rgba(0, 0, 0, 0.30);
  width: 85%;
  height: 100%;
  padding: 3rem;
  border-radius: 1rem;
  box-shadow: rgba(60, 64, 67, 0.3) 0px 1px 2px 0px, rgba(60, 64, 67, 0.15) 0px 2px 6px 2px;
}

.slider-professional {
  overflow-x: scroll;
  scroll-snap-type: x mandatory;
  display: flex;
  column-gap: 2rem;
  width: 100%;
  padding-bottom: 1rem;
}

.slider-professional::-webkit-scrollbar {
  display: none;
  width: 0;
}
</style> 