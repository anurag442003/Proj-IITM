<template>
    <div class="content-card">
        <img :src="decodedImage" alt="Content Image" @error="handleImageError" />
        <div class="content-body">
            <div class="title-section">
                <p>Title</p>
                <h3>{{ content.title }}</h3>
            </div>
            <div class="details-section">
                <p>Author: {{ content.author }}</p>
                <p>Rating: {{ isNaN(content.rating) ? 'N/A' : content.rating.toFixed(2) }} / 5</p>
            </div>
            <div class="action-buttons">
                <button class="btn btn-primary btn-sm" @click="editContent(content.id)">
                    <i class="fa-solid fa-pen"></i> Edit
                </button>
                <router-link class="btn btn-success btn-sm" :to="'/activity-data/' + content.id">
                    <i class="fa-solid fa-chart-line"></i> View Activity
                </router-link>
                <button class="btn btn-danger btn-sm" @click="confirmDeletion(content.id)">
                    <i class="fa-solid fa-trash"></i> Delete
                </button>
            </div>
            <div v-if="showAlert" :class="[alertType, 'alert-dismissible', 'fade', 'show']" role="alert">
                {{ alertMessage }}
                <button type="button" class="btn-close" @click="closeAlert" aria-label="Close"></button>
            </div>
        </div>

        <AlertTop v-if="showAlert" :message="alertMessage" :type="alertType" @close="closeAlert" />
    </div>
</template>

<script>
import AlertTop from './Mad2_AlertTop.vue';

export default {
    components: {
        AlertTop,
    },
    data() {
        return {
            showAlert: false,
            alertType: 'success',
            alertMessage: '',
        };
    },
    props: {
        content: {
            type: Object,
            required: true,
        },
        decodedImage: {
            type: String,
            required: true,
        },
    },
    methods: {
        confirmDeletion(contentId) {
            if (confirm("Are you sure you want to delete this content?")) {
                this.removeContent(contentId);
            }
        },
        getDecodedImage(content) {
            return `data:image/${content.imageType};base64,${content.image}`;
        },
        handleImageError(event) {
            console.error("Image failed to load:", event);
        },
        navigateToActivity(contentId) {
            this.$router.push(`/activity-data/${contentId}`);
        },
        filterContentsBySection(sectionId) {
            return this.contents
                .filter(content => content.section === sectionId)
                .map(content => ({
                    ...content,
                    decodedImage: this.getDecodedImage(content),
                    rating: this.calculateAverageRating(content.id),
                }));
        },
        editContent(contentId) {
            this.$router.push({ name: 'EditContent', params: { contentId } });
        },
        removeContent(contentId) {
            const token = sessionStorage.getItem('token');

            fetch(`http://127.0.0.1:5000/delete-content/${contentId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
            })
                .then(response => {
                    if (response.ok) {
                        this.showAlert = true;
                        this.alertType = 'success';
                        this.alertMessage = 'Content successfully deleted.';
                        return response.json();
                    } else {
                        throw new Error('Failed to delete content');
                    }
                })
                .then(data => {
                    this.$emit('contentUpdated');
                    console.log(data.message);
                })
                .catch(error => {
                    this.showAlert = true;
                    this.alertType = 'error';
                    this.alertMessage = 'Content deletion failed.';
                    console.error(error);
                });
        },
        closeAlert() {
            this.showAlert = false;
        }
    }
};
</script>

<style scoped>
.content-card {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    background-color: #f3eeee;
    border-radius: 0.5rem;
    border: 1px solid white;
    box-shadow: 0 50px 100px -20px rgba(50, 50, 93, 0.25), 0 30px 60px -30px rgba(0, 0, 0, 0.3), 0 -2px 6px 0 rgba(10, 37, 64, 0.35) inset;
    width: 210px;
    scroll-snap-align: start;
}

.content-card img {
    height: 180px !important;
    border-radius: 0.5rem 0.5rem 0 0;
    width: auto;
}

.content-body {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 0.5rem;
    height: 100%;
}

.title-section {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
    font-family: Arial, Helvetica, sans-serif;
}

.title-section p {
    font-size: 14px;
    line-height: 18px;
    color: #333;
    margin: 0;
}

.title-section h3 {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 20px;
    line-height: 30px;
    margin: 0;
    color: black;
    width: 200px;
}

.details-section {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    width: 100%;
}

.details-section p {
    font-size: 14px;
    line-height: 18px;
    color: #333;
    margin: 0;
}

.action-buttons {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-top: auto;
}

.action-buttons button {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.5rem;
    width: 100%;
}
</style>
