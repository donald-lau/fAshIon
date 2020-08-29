<template>
    <div>
        <hero></hero>
        <predict></predict>
    </div>
</template>
<script>
import Hero from "./components/Hero";
import Predict from "./components/Predict"

export default {
  name: "components",
  components: {
    Hero,
    Predict,
  }
};
</script>
