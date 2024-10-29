<template>
    <div class="custom-container">
        <section class="single-container">
            <div class="wrapper" v-for="service in services" :key="service.id">
                <h2 class="my2">{{ service.name }}</h2>
                <h4 class="my3">Time required : {{ service.time }} hours</h4>
                <h4 class="my3">Base Price : {{ service.baseprice }} Rs.</h4>
                <div class="slider-professional">
                    <professional-card v-for="professional in filteredProfessionals(service.id)" :key="professional.id" :professional="professional"
                        :decodedImage="professional.decodedImage" :isRead="false"></professional-card>
                </div>
            </div>
        </section>
    </div>
</template>

<script>
import ProfessionalCard from './Mad2_ProfessionalCard.vue';

export default {
    components: {
        ProfessionalCard,
    },
    data() {
        return {
            InDemand: [],
            professionals: [],
            services: [],
            selectedService: null,
            selectedProfessional: null,
            isCreatingService: true,
            loadingServiceProfessional: false,
            cardWidthPercentage: 20,
        };
    },
    mounted() {
        this.fetchInDemandProfessionals();
        this.fetchServices();
        this.fetchProfessionals();
    },
    methods: {
        filteredProfessionals(serviceId) {
            return this.professionals
                .filter(professional => professional.service === serviceId)
                .map(professional => ({
                    ...professional,
                    decodedImage: this.getDecodedImage(professional),
                }));
        },
        async fetchProfessionals() {
            try {
                const response = await this.$axios.get(`http://127.0.0.1:5000/fetch-professional`);
                this.professionals = response.data.professionals;
            } catch (error) {
                console.error('Error fetching user professionals:', error);
            }
        },
        async fetchServices() {
            this.loadingServiceProfessional = true;
            try {
                const response = await this.$axios.get('http://127.0.0.1:5000/fetch-services');
                this.services = response.data.services;
            } catch (error) {
                console.error('Error fetching services:', error);
            } finally {
                this.loadingServiceProfessional = false;
            }
        },
        async fetchInDemandProfessionals() {
            try {
                const response = await this.$axios.get(`http://127.0.0.1:5000/fetch-InDemand`);
                this.InDemand = response.data.professionals;
            } catch (error) {
                console.error('Error fetching InDemand professionals:', error);
            }
        },
        getDecodedImage(professional) {
            const decodedImage = `data:image/${professional.imageType};base64, ${professional.image}`;
            return decodedImage;
        },
    },
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
    background-color: rgba(0, 0, 0, 0.30);
    width: 85%;
    height: 100%;
    padding: 3rem;
    border-radius: 1rem;
    box-shadow: rgba(60, 64, 67, 0.3) 0px 1px 2px 0px, rgba(60, 64, 67, 0.15) 0px 2px 6px 2px;
}

.wrapper {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    width: 100%;
    overflow: hidden;
}

.wrapper h2 {
    font-size: 30px;
    line-height: 44px;
    color: wheat;
    font-weight: 700;
    font-family: Arial, Helvetica, sans-serif;
    border-bottom: 2px solid rgb(255, 251, 251);
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
