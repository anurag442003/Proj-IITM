<template>
  <div class="custom-container margin-top text-center mb-2">
    <div v-if="errorMessage" class="alert alert-danger mt-3">
      {{ errorMessage }}
    </div>
    <div v-if="successMessage" class="alert alert-success mt-3">
      {{ successMessage }}
    </div>
    <h2 class="mb-4">Register</h2>
    <form @submit.prevent="registerUser">
      <!-- First row -->
      <div class="row">
        <div class="col-md-3 mb-3">
          <label for="firstname" class="form-label">First Name:</label>
          <input v-model="userData.firstname" type="text" class="form-control" required />
        </div>
        <div class="col-md-3 mb-3">
          <label for="lastname" class="form-label">Last Name:</label>
          <input v-model="userData.lastname" type="text" class="form-control" required />
        </div>
        <div class="col-md-3 mb-3">
          <label for="username" class="form-label">Username:</label>
          <input v-model="userData.username" type="text" class="form-control" required />
          <div v-if="validationErrors.username" class="text-danger">
            {{ validationErrors.username }}
          </div>
        </div>
        <div class="col-md-3 mb-3">
          <label for="phoneNumber" class="form-label">Phone Number:</label>
          <input v-model="userData.phoneNumber" type="tel" class="form-control" required />
        </div>
      </div>

      <!-- Second row -->
      <div class="row">
        <div class="col-md-3 mb-3">
          <label for="gender" class="form-label">Gender:</label>
          <select v-model="userData.gender" class="form-select" required>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div class="col-md-3 mb-3">
          <label for="city" class="form-label">City:</label>
          <input v-model="userData.city" type="text" class="form-control" required />
        </div>
        <div class="col-md-3 mb-3">
          <label for="email" class="form-label">Email:</label>
          <input v-model="userData.email" type="email" class="form-control" required />
        </div>
        <div class="col-md-3 mb-3">
          <label for="password" class="form-label">Password:</label>
          <input v-model="userData.password" type="password" class="form-control" required />
          <div v-if="validationErrors.password" class="text-danger">
            {{ validationErrors.password }}
          </div>
        </div>
      </div>

      <!-- Third row -->
      <div class="row">
        <div class="col-md-4 mb-3">
          <label for="state" class="form-label">State:</label>
          <input v-model="userData.state" type="text" class="form-control" required />
          <div v-if="validationErrors.state" class="text-danger">
            {{ validationErrors.state }}
          </div>
        </div>
        <div class="col-md-4 mb-3">
          <label for="zip" class="form-label">ZIP Code:</label>
          <input v-model="userData.zip" type="text" class="form-control" required />
        </div>
        <div class="col-md-4 mb-3">
          <label for="address" class="form-label">House Number:</label>
          <input v-model="userData.address" type="text" class="form-control" required />
        </div>
      </div>

      <!-- Role selection -->
      <div class="row">
        <div class="mb-3">
          <label for="role" class="form-label">Role:</label>
          <div class="btn-group visibility col-12 pt-3 px-2 py-2" role="group">
            <input v-model="userData.role" type="radio" class="btn-check" name="btnradio" id="btnradio1" value="READER">
            <label class="btn btn-outline-primary" for="btnradio1"><b>READER</b></label>

            <input v-model="userData.role" type="radio" class="btn-check" name="btnradio" id="btnradio2" value="LIBRARIAN">
            <label class="btn btn-outline-success" for="btnradio2"><b>LIBRARIAN</b></label>
          </div>
        </div>
      </div>

      <!-- Additional fields for Librarian -->
      <div v-if="userData.role === 'LIBRARIAN'">
        <div class="row">
          <div class="col-md-3 mb-3">
            <label for="experience" class="form-label">Experience (in years):</label>
            <input v-model="userData.experience" type="number" class="form-control" required />
          </div>
          <div class="col-md-3 mb-3">
            <label for="publishYear" class="form-label">Publish Year:</label>
            <input v-model="userData.publish_year" type="date" class="form-control" required />
          </div>
          <div class="col-md-3 mb-3">
            <label for="additionalCharges" class="form-label">Additional Charges:</label>
            <input v-model="userData.additionalCharges" type="number" step="0.01" class="form-control" required />
          </div>
          <div class="col-md-3 mb-3">
            <label for="resume" class="form-label">Resume:</label>
            <input type="file" @change="handleResumeUpload" class="form-control" accept=".pdf,.doc,.docx" required />
          </div>
        </div>
        <div class="row">
          <div class="col-md-4 mb-3">
            <label for="description" class="form-label">Description:</label>
            <textarea v-model="userData.description" class="form-control" required></textarea>
          </div>
          <div class="col-md-4 mb-3">
            <label for="image" class="form-label">Profile Image:</label>
            <input type="file" @change="handleImageUpload" class="form-control" accept="image/*" required />
          </div>
          <div class="col-md-4 mb-3">
            <label for="serviceType" class="form-label">Service:</label>
            <select v-model="userData.serviceType" class="form-select" required>
              <option v-for="service in services" :key="service.id" :value="service.id">
                {{ service.name }} - ({{ service.price}}Rs.)
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- Submit button -->
      <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
        {{ isSubmitting ? 'Registering...' : 'Register' }}
      </button>
    </form>
    
    <div class="mt-3 text-center">
      Existing User? <router-link to="/login" class="btn btn-sm btn-dark">LOGIN</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserRegistration',
  data() {
    return {
      userData: {
        firstname: '',
        lastname: '',
        username: '',
        phoneNumber: '',
        gender: 'male',
        city: '',
        email: '',
        password: '',
        state: '',
        zip: '',
        address: '',
        role: 'READER',
        experience: '',
        additionalCharges: '',
        publish_year: '',
        description: '',
        resume: null,
        image: null,
        serviceType: ''
      },
      services: [],
      validationErrors: {},
      successMessage: '',
      errorMessage: '',
      isSubmitting: false
    };
  },
  async created() {
    try {
      const response = await this.$axios.get('http://127.0.0.1:5000/fetch-service_names');
      this.services = response.data.services;
    } catch (error) {
      console.error('Error fetching services:', error);
      this.errorMessage = 'Failed to load services';
    }
  },
  methods: {
    validateForm() {
      this.validationErrors = {};
      
      if (this.userData.username.length > 20) {
        this.validationErrors.username = 'Username must be at most 20 characters long.';
      }

      const passwordRegex = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()-_+=]).{8,}$/;
      if (!passwordRegex.test(this.userData.password)) {
        this.validationErrors.password =
          'Password must be at least 8 characters long and contain at least one lowercase letter, one uppercase letter, one digit, and one special character.';
      }

      const stateRegex = /^[a-zA-Z\s]*$/;
      if (!stateRegex.test(this.userData.state)) {
        this.validationErrors.state = 'State name can only contain alphabets and spaces.';
      }

      const phoneRegex = /^\d{10}$/;
      if (!phoneRegex.test(this.userData.phoneNumber)) {
        this.validationErrors.phoneNumber = 'Phone number must be 10 digits.';
      }

      return Object.keys(this.validationErrors).length === 0;
    },

    handleResumeUpload(event) {
      const file = event.target.files[0];
      if (file) {
        const allowedTypes = ['.pdf', '.doc', '.docx'];
        const fileExtension = file.name.toLowerCase().slice((file.name.lastIndexOf(".") - 1 >>> 0) + 2);
        if (!allowedTypes.includes('.' + fileExtension)) {
          this.errorMessage = 'Please upload a valid document file (PDF, DOC, or DOCX)';
          event.target.value = '';
          return;
        }
        if (file.size > 5 * 1024 * 1024) {
          this.errorMessage = 'File size should not exceed 5MB';
          event.target.value = '';
          return;
        }
        this.userData.resume = file;
      }
    },

    handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
        if (!allowedTypes.includes(file.type)) {
          this.errorMessage = 'Please upload a valid image file (JPEG, PNG, or GIF)';
          event.target.value = '';
          return;
        }
        if (file.size > 2 * 1024 * 1024) { 
          this.errorMessage = 'Image size should not exceed 2MB';
          event.target.value = '';
          return;
        }
        this.userData.image = file;
      }
    },

    async registerUser() {
      try {
        if (!this.validateForm()) {
          return;
        }

        this.isSubmitting = true;
        this.errorMessage = '';
        this.successMessage = '';

        const formData = new FormData();
        
        Object.keys(this.userData).forEach(key => {
          if (key !== 'resume' && key !== 'image') {
            if (key === 'publish_year' && this.userData[key]) {
              formData.append(key, new Date(this.userData[key]).getFullYear().toString());
            } else {
              formData.append(key, this.userData[key]);
            }
          }
        });
        
        if (this.userData.resume) {
          formData.append('resume', this.userData.resume);
        }
        if (this.userData.image) {
          formData.append('image', this.userData.image);
        }
        for (let pair of formData.entries()) {
          console.log(pair[0] + ': ' + pair[1]);
        }
        const response = await this.$axios.post('http://127.0.0.1:5000/register', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        if (response.status === 201) {
          this.successMessage = response.data.message;
          this.clearForm();
          setTimeout(() => {
            this.$router.push('/login');
          }, 1500);
        } else {
          this.errorMessage = response.data.error || 'Registration failed for unknown reasons.';
        }
      } catch (error) {
        console.error('Registration error:', error);
        this.errorMessage = error.response?.data?.error || 'An error occurred during registration.';
      } finally {
        this.isSubmitting = false;
      }
    },

    clearForm() {
      this.userData = {
        firstname: '',
        lastname: '',
        username: '',
        phoneNumber: '',
        gender: 'male',
        city: '',
        email: '',
        password: '',
        state: '',
        zip: '',
        address: '',
        role: 'READER',
        is_active: 1,
        experience: '',
        additionalCharges: '',
        publish_year: '',
        description: '',
        resume: null,
        image: null,
        serviceType: ''
      };
      this.validationErrors = {};
      this.errorMessage = '';
      this.successMessage = '';
    }
  }
};
</script>

<style scoped>
.custom-container {
  border-radius: 1rem;
  max-width: 900px;
  margin: auto;
  background-color: rgba(0, 0, 0, 0.3);
  color: #000000;
  padding: 15px;
}

.margin-top {
  margin-top: 90px;
}

.form-label {
  font-weight: bold;
}

.form-control,
.form-select {
  margin-bottom: 15px;
}

.btn-primary {
  width: 100%;
}

.btn {
  border-radius: 15px;
}

/* Add loading state styles */
.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Add responsive styles */
@media (max-width: 768px) {
  .custom-container {
    margin-top: 20px;
    padding: 10px;
  }
  
  .row {
    margin-right: -5px;
    margin-left: -5px;
  }
  
  .col-md-3,
  .col-md-4 {
    padding-right: 5px;
    padding-left: 5px;
  }
}
</style>