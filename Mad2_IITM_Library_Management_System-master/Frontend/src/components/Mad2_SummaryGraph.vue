<template>
    <div class="custom-container d-flex">
        <div class="graph">
            <h2>Services offered per type</h2>
            <img ref="serviceChart" class="service-chart" alt="Service Reader Count">
        </div>
        <div class="graph">
            <h2>Professional gender distribution</h2>
            <img ref="genderChart" class="gender-chart" alt="Professional gender distribution">
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            serviceData: [],
            serviceNames: [],
            readerCounts: [],
        };
    },
    methods: {
        async fetchReaderCountPerService() {
            try {
                const response = await fetch('http://127.0.0.1:5000/count_per_service', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${sessionStorage.getItem('token')}`,
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch data');
                }

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                this.$refs.serviceChart.src = url;
                console.log('Service Chart loaded');
                setTimeout(() => {
                    this.fetchReaderCountGender();
                }, 0);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        },
        async fetchReaderCountGender() {
            try {
                const response = await fetch('http://127.0.0.1:5000/user_count_gender', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${sessionStorage.getItem('token')}`,
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch data');
                }

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                this.$refs.genderChart.src = url;
                console.log('Gender Chart loaded');
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        },
    },
    created() {
        this.fetchReaderCountPerService();
    },
};
</script>

<style scoped>
.custom-container {
    margin: 60px auto;
    color: rgba(13, 230, 129, 0.95);
    display: flex;
    justify-professional: center;
    gap: 3rem;
    flex-wrap: wrap;
}

h2 {
    font-size: 1.5rem;
    margin-bottom: 10px;
    text-align: center;
}

.service-chart,
.gender-chart {
    border-radius: 5px;
    height: 400px;
    width: 100%; 
    max-width: 400px;
}

.graph {
    box-shadow: rgba(0, 0, 0, 0.17) 0px -23px 25px 0px inset, rgba(0, 0, 0, 0.15) 0px -36px 30px 0px inset, rgba(0, 0, 0, 0.1) 0px -79px 40px 0px inset, rgba(0, 0, 0, 0.06) 0px 2px 1px, rgba(0, 0, 0, 0.09) 0px 4px 2px, rgba(0, 0, 0, 0.09) 0px 8px 4px, rgba(0, 0, 0, 0.09) 0px 16px 8px, rgba(0, 0, 0, 0.09) 0px 32px 16px;
}
</style>
