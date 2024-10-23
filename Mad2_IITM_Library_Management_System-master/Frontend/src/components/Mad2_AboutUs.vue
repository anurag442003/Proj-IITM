<template>
    <div class="about-container">
        <h2>About The Wisdom</h2>
        <p>Your ultimate destination for seamless library management!</p>

        <section>
            <h3>Our Vision</h3>
            <p>
                At The Wisdom, we strive to deliver an intuitive and effective library management system that caters to both librarians and book lovers.
            </p>
        </section>

        <section>
            <h3>Founder</h3>
            <ul>
                <li><strong>Vikas Jha</strong> - 23f1001674@ds.study.iitm.ac.in</li>
            </ul>
        </section>

        <section>
            <h3>Get in Touch</h3>
            <p>If you have any inquiries or feedback, we’d love to hear from you:</p>
            <p>Email: support@thewisdom.com</p>
        </section>
    </div>
</template>
  
<script>
export default {
    name: 'Mad2_AboutUs',
};
</script>
  
<style scoped>
.about-container {
    max-width: 700px;
    margin: 0 auto;
    padding: 25px;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

h2 {
    font-size: 2.5em;
    color: #2c3e50;
    margin-bottom: 15px;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
}

h3 {
    font-size: 1.8em;
    color: #34495e;
    margin-bottom: 10px;
}

p {
    line-height: 1.8;
    color: #7f8c8d;
    margin-bottom: 15px;
}

ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

li {
    margin-bottom: 10px;
    color: #2980b9;
}

section {
    margin-bottom: 25px;
    padding: 10px;
    background-color: #ecf0f1;
    border-radius: 5px;
}

footer {
    margin-top: 40px;
    text-align: center;
    color: #95a5a6;
}
</style>
