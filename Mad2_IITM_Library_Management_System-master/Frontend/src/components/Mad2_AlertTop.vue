<template>
    <div v-if="isVisible" :class="['alert', alertClass]">
        <p>{{ message }}</p>
    </div>
</template>

<script>
export default {
    props: {
        message: {
            type: String,
            required: true
        },
        type: {
            type: String,
            default: 'error'
        }
    },
    data() {
        return {
            isVisible: true
        };
    },
    computed: {
        alertClass() {
            return `alert-${this.type}`;
        }
    },
    methods: {
        closeAlert() {
            this.isVisible = false;
        }
    },
    mounted() {
        // Automatically hide the alert after 5 seconds if needed
        // setTimeout(() => {
        //     this.closeAlert();
        // }, 5000);
    }
};
</script>

<style scoped>
.alert {
    padding: 10px 20px;
    margin-bottom: 20px;
    border: 1px solid transparent;
    border-radius: 4px;
}

.alert-error {
    background-color: #f8d7da;
    border-color: #f5c6cb;
    color: #721c24;
}
</style>
