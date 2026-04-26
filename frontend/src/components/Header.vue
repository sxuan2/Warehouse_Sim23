<template>
  <header>
    <div class="logo">
      <img :src="logoUrl" alt="Company Logo" />
    </div>
    <h1>{{ companyName }}</h1>
    <h2>3PL Warehouse Simulator</h2>
    <input type="file" @change="onLogoUpload" accept="image/*" />
    <input v-model="companyName" placeholder="Enter Company Name" />
  </header>
</template>

<script>
export default {
  name: 'Header',
  data() {
    return {
      logoUrl: '/path/to/logo.png', // Update this path to your logo
      companyName: 'Your Company Name', // Set your company name here
    };
  },
  methods: {
    onLogoUpload(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.logoUrl = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    },
  },
};
</script>

<style scoped>
header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  background-color: #f8f9fa;
}
.logo img {
  height: auto;
  max-height: 50px;
  max-width: 100%;
  object-fit: cover;
}
h1, h2 {
  margin: 0;
}
input {
  margin-left: 10px;
}
</style>