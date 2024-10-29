<template>
    <div class="professional">
        <!-- <button v-if="isLoggedIn()" class="btn btn-sm btn-light top-btn" @click="confirmPurchase(professional.id)">
            <i class="fa-solid fa-download"></i>
        </button> -->
        <img :src="decodedImage" alt="Professional Image" @error="handleImageError" />
        <div class="body">
            <div class="title-holder">
                <!-- <p>Title</p> -->
                <h3>{{ professional.title }}</h3>
                <p>About me: {{ professional.prof_desc }}</p>
                <p>Service Charge: {{ professional.price }} </p>

            </div>
            <div class="bottom-area">
                <p>Rating: {{ !professional.rating || isNaN(professional.rating) ? 'N/A' : `${professional.rating.toFixed(2)} / 5` }}</p>
            </div>
            <div class="text-center" v-if="professional.isIssued">
                <router-link :to="{ name: 'RateProfessional', params: { professionalId: professional.id } }" class="btn btn-warning btn-sm">
                    Rate <i class="fa-regular fa-star"></i>
                </router-link>
            </div>
            <div class="button-grid">
                <button v-if="!professional.isIssued && !professional.isRequested " class="btn btn-primary btn-sm" @click="createRequest(professional.id)">
                    <i class="fa-solid fa-prof"></i> Request
                </button>
                <div v-if="professional.isRequested && !professional.isIssued" class="btn btn-secondary btn-sm">
                    <i class="fa-solid fa-hourglass-start"></i> Waiting
                </div>
                <!-- <button v-show="professional.isIssued" class="btn btn-primary btn-sm" @click="openProfessional(professional.id)">
                    <i class="fa-brands fa-readme"></i> Read
                </button> -->
                <button v-show="professional.isIssued" class="btn btn-danger btn-sm" @click="returnProfessional(professional.id)">
                    <i class="fa-solid fa-rotate-left"></i> End service
                </button>
                <!--<button class="btn btn-light btn-sm"
                        @click="toggleWishlist(professional.id, professional.isWishlisted)"
                        :class="{ 'btn-danger': professional.isWishlisted, 'btn-warning': !professional.isWishlisted }">
                    <i class="fa-regular fa-heart" :class="{ 'fas': professional.isWishlisted }"></i> Wishlist
                </button>-->
            </div>
        </div>
    </div>
</template>

<script>
export default {
    props: {
        professional: {
            type: Object,
            required: true,
        },
        decodedImage: {
            type: String,
            required: true,
        },
    },
    methods: {
        // confirmPurchase(professionalId) {
        //     if (confirm("Are you sure you want to purchase/download this professional?")) {
        //         this.buyDownload(professionalId);
        //     }
        // },
        async createRequest(professionalId) {
            if (!this.isLoggedIn()) {
                this.$router.push('/login');
                return;
            }

            try {
                await this.$axios.post(`http://127.0.0.1:5000/create_request/${professionalId}`, null, {
                    headers: {
                        Authorization: `Bearer ${sessionStorage.getItem('token')}`,
                    },
                });
                this.$emit('professionalUpdated');
                console.log('Request created successfully.');
            } catch (error) {
                console.error('Error creating request:', error);
            }
        },
        async openProfessional(professionalId) {
            try {
                const response = await fetch(`http://127.0.0.1:5000/get_pdf/${professionalId}`, {
                    headers: {
                        Authorization: `Bearer ${sessionStorage.getItem('token')}`,
                    },
                });
                const blob = await response.blob();

                const pdfUrl = URL.createObjectURL(blob);

                window.open(pdfUrl, '_blank');
            } catch (error) {
                console.error('Error opening professional:', error);
            }
        },
        async returnProfessional(professionalId) {
            try {
                await this.$axios.post(`http://127.0.0.1:5000/return_professional/${professionalId}`, null, {
                    headers: {
                        Authorization: `Bearer ${sessionStorage.getItem('token')}`,
                    },
                });
                this.$emit('professionalUpdated');
            } catch (error) {
                console.error('Error returning professional:', error);
            }
        },
        // async toggleWishlist(professionalId, isInWishlist) {
        //     if (!this.isLoggedIn()) {
        //         this.$router.push('/login');
        //         return;
        //     }

        //     try {
        //         const endpoint = isInWishlist ? 'remove' : 'add';
        //         const response = await this.$axios.post(`http://127.0.0.1:5000/wishlist/${endpoint}/${professionalId}`, null, {
        //             headers: {
        //                 Authorization: `Bearer ${sessionStorage.getItem('token')}`,
        //             },
        //         });

        //         this.$emit('professionalUpdated');

        //         console.log(response.data);
        //     } catch (error) {
        //         console.error('Error toggling wishlist:', error);
        //     }
        // },
        // async buyDownload(professionalId) {
        //     if (!this.isLoggedIn()) {
        //         this.$router.push('/login');
        //         return;
        //     }

        //     try {
        //         const response = await this.$axios.get(`http://127.0.0.1:5000/download_purchase/${professionalId}`, {
        //             responseType: 'blob',
        //             headers: {
        //                 Authorization: `Bearer ${sessionStorage.getItem('token')}`,
        //             },
        //         });

        //         const blob = new Blob([response.data], { type: 'application/pdf' });
        //         const url = window.URL.createObjectURL(blob);

        //         const link = document.createElement('a');
        //         link.href = url;
        //         link.setAttribute('download', `${this.professional.pdf_file_name}`);
        //         document.body.appendChild(link);
        //         link.click();

        //         window.URL.revokeObjectURL(url);
        //         document.body.removeChild(link);
        //     } catch (error) {
        //         console.error('Error purchasing and downloading professional:', error);
        //     }
        // },
        handleImageError(event) {
            console.error("Error loading image:", event);
        },
        isLoggedIn() {
            return !!sessionStorage.getItem('token');
        },
    },
};
</script>

<style scoped>
.professional {
    position: relative;
    display: flex;
    flex-direction: column;
    row-gap: 0.5rem;
    background-color: rgb(243, 238, 238);
    border-radius: 0.5rem;
    border: 1px solid white;
    box-shadow: rgba(50, 50, 93, 0.25) 0px 50px 100px -20px, rgba(0, 0, 0, 0.3) 0px 30px 60px -30px, rgba(10, 37, 64, 0.35) 0px -2px 6px 0px inset;
    width: 210px;
    z-index: 1;
    scroll-snap-align: start;
}

.professional img {
    height: 180px !important;
    border-radius: 0.5rem 0.5rem 0 0;
    width: auto;
}

.professional .body {
    display: flex;
    flex-direction: column;
    row-gap: 0.5rem;
    padding: 0.5rem;
    height: 100%;
}

.title-holder {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    row-gap: 0.25rem;
    font-family: Arial, Helvetica, sans-serif;
}

.title-holder p {
    font-size: 14px;
    line-height: 18px;
    color: rgb(51, 51, 51);
    margin: unset;
}

.title-holder h3 {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 20px;
    line-height: 30px;
    margin: unset;
    color: black;
    width: 200px;
}

.bottom-area {
    display: flex;
    flex-direction: column;
    justify-professional: flex-start;
    row-gap: 0.25rem;
    width: 100%;
}

.bottom-area p {
    font-size: 14px;
    line-height: 18px;
    color: rgb(51, 51, 51);
    margin: unset;
}

.button-grid {
    gap: 0.5rem;
    display: flex;
    justify-professional: center;
    margin-top: auto;
}

.button-grid button {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    padding: 0.5rem;
    width: 100%;
}

.text-center .btn {
    width: -moz-available;
}

.top-btn {
    position: absolute;
    top: 5px;
    right: 5px;
}
</style>
