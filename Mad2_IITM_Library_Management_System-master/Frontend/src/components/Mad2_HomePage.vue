<template>
    <div class="custom-container">
        <section class="single-container">
            <div class="wrapper" v-for="service in services" :key="service.id">
                <h2 class="my2">{{ service.name }}</h2>
                <h4 class="my3">Time required : {{ service.time }} hours</h4>
                <h4 class="my3">Base Price : {{ service.baseprice }} Rs.</h4>
                <div class="slider-content">
                    <content-card v-for="content in filteredContents(service.id)" :key="content.id" :content="content"
                        :decodedImage="content.decodedImage" :isRead="false"></content-card>
                </div>
            </div>
        </section>
    </div>
</template>

<script>
import ContentCard from './Mad2_ContentCard.vue';

export default {
    components: {
        ContentCard,
    },
    data() {
        return {
            InDemand: [],
            contents: [],
            services: [],
            selectedService: null,
            selectedContent: null,
            isCreatingService: true,
            loadingServiceContent: false,
            cardWidthPercentage: 20,
        };
    },
    mounted() {
        this.fetchInDemandContents();
        this.fetchServices();
        this.fetchContents();
    },
    methods: {
        filteredContents(serviceId) {
            return this.contents
                .filter(content => content.service === serviceId)
                .map(content => ({
                    ...content,
                    decodedImage: this.getDecodedImage(content),
                }));
        },
        async fetchContents() {
            try {
                const response = await this.$axios.get(`http://127.0.0.1:5000/fetch-content`);
                this.contents = response.data.contents;
            } catch (error) {
                console.error('Error fetching user contents:', error);
            }
        },
        async fetchServices() {
            this.loadingServiceContent = true;
            try {
                const response = await this.$axios.get('http://127.0.0.1:5000/fetch-services');
                this.services = response.data.services;
            } catch (error) {
                console.error('Error fetching services:', error);
            } finally {
                this.loadingServiceContent = false;
            }
        },
        async fetchInDemandContents() {
            try {
                const response = await this.$axios.get(`http://127.0.0.1:5000/fetch-InDemand`);
                this.InDemand = response.data.contents;
            } catch (error) {
                console.error('Error fetching InDemand contents:', error);
            }
        },
        getDecodedImage(content) {
            const decodedImage = `data:image/${content.imageType};base64, ${content.image}`;
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

.slider-content {
    overflow-x: scroll;
    scroll-snap-type: x mandatory;
    display: flex;
    column-gap: 2rem;
    width: 100%;
    padding-bottom: 1rem;
}

.slider-content::-webkit-scrollbar {
    display: none;
    width: 0;
}
</style>
