<template>
    <div class="custom-container">
        <section class="single-container">
            <div class="wrapper" v-for="service in services" :key="service.id">
                <div class="service-head">
                    <h2 class="my2">{{ service.name }}</h2>
                    <h4 class="my3">Time required : {{ service.time }} hours</h4>
                    <h4 class="my3">  Base Price : {{ service.baseprice }} Rs.</h4>
                    <div class="service-btn">
                        <router-link :to="'/update-service/' + service.id" class="btn btn-sm btn-primary"><i class="fa-regular fa-pen-to-square"></i></router-link>
                        <!-- <router-link :to="'/upload-content/' + service.id" class="btn btn-sm btn-success"><i class="fa-solid fa-plus"></i></router-link> -->
                        <button @click="confirmDelete(service.id)" class="btn btn-sm btn-danger"><i class="fa-solid fa-trash"></i></button>
                    </div>
                </div>
                <div class="slider-content">
                    <admin-content-card v-for="content in filteredContents(service.id)" :key="content.id"
                        :content="content" :decodedImage="content.decodedImage"
                        @content-updated="updatedContent"></admin-content-card>
                </div>
            </div>
        </section>
        <BottomNav/>
    </div>
</template>

<script>
import BottomNav from './Mad2_BottomNav.vue';
import AdminContentCard from './Mad2_AdminContentCard.vue';

export default {
    components: {
        BottomNav,
        AdminContentCard,
    },
    data() {
        return {
            contents: [],
            services: [],
        };
    },
    created() {
        this.fetchContents();
        this.fetchServices();
    },
    methods: {
        updatedContent() {
            this.fetchContents();
        },
        fetchContents() {
            fetch('http://127.0.0.1:5000/fetch-content')
                .then(response => response.json())
                .then(data => {
                    this.contents = data.contents;
                    this.contents.forEach(content => {
                        if (content.isRead) {
                            this.$store.dispatch('setContentRead', { contentId: content.id, isRead: true });
                        }
                        // if (content.isWishlisted) {
                        //     this.$store.dispatch('toggleContentWishlist', { contentId: content.id, isWishlisted: true });
                        // }
                    });
                })
                .catch(error => {
                    console.error('Error fetching user contents:', error);
                });
        },
        fetchServices() {
            fetch('http://127.0.0.1:5000/fetch-services')
                .then(response => response.json())
                .then(data => {
                    this.services = data.services;
                })
                .catch(error => {
                    console.error('Error fetching services:', error);
                });
        },
        getDecodedImage(content) {
            const decodedImage = `data:image/${content.imageType};base64, ${content.image}`;
            return decodedImage;
        },
        filteredContents(serviceId) {
            return this.contents
                .filter(content => content.service === serviceId)
                .map(content => ({
                    ...content,
                    decodedImage: this.getDecodedImage(content),
                }));
        },
        deleteService(serviceId) {
            const token = sessionStorage.getItem('token');
            fetch(`http://127.0.0.1:5000/remove-service/${serviceId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
            })
                .then(response => {
                    if (response.ok) {
                        this.services = this.services.filter(service => service.id !== serviceId);
                        return response.json();
                    } else {
                        throw new Error('Failed to delete service');
                    }
                })
                .then(data => {
                    console.log(data.message);
                })
                .catch(error => {
                    console.error('Error deleting service:', error);
                });
        },
        confirmDelete(serviceId) {
            if (confirm("Are you sure you want to delete this service?")) {
                this.deleteService(serviceId);
            }
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

.service-head {
    display: flex;
    align-items: center;
}

.service-head h2 {
    margin-right: 30px;
    color: white;
    font-size: 24px;
    font-weight: bold;
    border-bottom: 2px solid lightgray;
}

.service-btn {
    display: flex;
    align-items: center;
    column-gap: 1rem;
}

.slider-content {
    display: flex;
    overflow-x: auto;
    gap: 2rem;
    scroll-snap-type: x mandatory;
}

.slider-content::-webkit-scrollbar {
    display: none;
    width: 0;
}
</style>
