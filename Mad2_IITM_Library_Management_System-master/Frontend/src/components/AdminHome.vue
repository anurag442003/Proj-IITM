<template>
    <div class="custom-container">
        <section class="single-container">
            <div class="wrapper" v-for="section in sections" :key="section.id">
                <div class="section-head">
                    <h2 class="my2">{{ section.name }}</h2>
                    <div class="section-btn">
                        <router-link :to="'/update-section/' + section.id" class="btn btn-sm btn-primary"><i class="fa-regular fa-pen-to-square"></i></router-link>
                        <router-link :to="'/upload-content/' + section.id" class="btn btn-sm btn-success"><i class="fa-solid fa-plus"></i></router-link>
                        <button @click="confirmDelete(section.id)" class="btn btn-sm btn-danger"><i class="fa-solid fa-trash"></i></button>
                    </div>
                </div>
                <div class="slider-content">
                    <admin-content-card v-for="content in filteredContents(section.id)" :key="content.id"
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
            sections: [],
        };
    },
    created() {
        this.fetchContents();
        this.fetchSections();
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
                        if (content.isWishlisted) {
                            this.$store.dispatch('toggleContentWishlist', { contentId: content.id, isWishlisted: true });
                        }
                    });
                })
                .catch(error => {
                    console.error('Error fetching user contents:', error);
                });
        },
        fetchSections() {
            fetch('http://127.0.0.1:5000/fetch-sections')
                .then(response => response.json())
                .then(data => {
                    this.sections = data.sections;
                })
                .catch(error => {
                    console.error('Error fetching sections:', error);
                });
        },
        getDecodedImage(content) {
            const decodedImage = `data:image/${content.imageType};base64, ${content.image}`;
            return decodedImage;
        },
        filteredContents(sectionId) {
            return this.contents
                .filter(content => content.section === sectionId)
                .map(content => ({
                    ...content,
                    decodedImage: this.getDecodedImage(content),
                }));
        },
        deleteSection(sectionId) {
            const token = sessionStorage.getItem('token');
            fetch(`http://127.0.0.1:5000/remove-section/${sectionId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
            })
                .then(response => {
                    if (response.ok) {
                        this.sections = this.sections.filter(section => section.id !== sectionId);
                        return response.json();
                    } else {
                        throw new Error('Failed to delete section');
                    }
                })
                .then(data => {
                    console.log(data.message);
                })
                .catch(error => {
                    console.error('Error deleting section:', error);
                });
        },
        confirmDelete(sectionId) {
            if (confirm("Are you sure you want to delete this section?")) {
                this.deleteSection(sectionId);
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

.section-head {
    display: flex;
    align-items: center;
}

.section-head h2 {
    margin-right: 30px;
    color: white;
    font-size: 24px;
    font-weight: bold;
    border-bottom: 2px solid lightgray;
}

.section-btn {
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
