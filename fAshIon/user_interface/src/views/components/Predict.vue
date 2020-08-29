<template>
    <section class="section pb-0 section-components">
        <div class="container mb-5">
            <!-- Inputs -->
            <div>
                <h3 class="h4 text-success font-weight-bold mb-4">
                    Start building your new outfit right here!
                </h3>
            </div>
            <hr>
            <div class="row">
                <div class="col-md-5">
                    <div class="row">
                        <div class="col-md-6">
                            <!--                <div item="col-md-3">-->
                            <strong>Color (optional)</strong>
                        </div>
                        <div class="col-md-6">
                            <strong>Material (optional)</strong>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <strong>Fashion Item (e.g. shirt)</strong>
                </div>
                <div class="col-md-4">
                    <strong>Image </strong>
                    <i class="fa fa-question-circle"
                       v-b-tooltip.hover.top title="Click on the image if you don't like the current image!"></i>
                </div>
            </div>
            <fashion-item ref="inputs"></fashion-item>
            <button type="button" class="btn btn-success" v-on:click="generate">Generate outfit</button>
            <button type="button" class="btn btn-success" v-on:click="saveOutfit">Save outfit</button>
            <div v-show="!isLoadingResult">
                <div v-show="isSubmitted">
                    <div class="row">
                        <div class="col-md-5">
                            <div class="row">
                                <div class="col-md-6">
                                    <!--                <div item="col-md-3">-->
                                    <strong>Color</strong>
                                </div>
                                <div class="col-md-6">
                                    <strong>Material</strong>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <strong>Fashion Item</strong>
                        </div>
                        <div class="col-md-2">
                            <strong>Image </strong>
                            <i class="fa fa-question-circle"
                               v-b-tooltip.hover.top
                               title="Click on the image if you don't like the current image!"></i>
                        </div>
                        <div class="col-md-2">
                            <strong>Select </strong>
                            <i class="fa fa-question-circle"
                               v-b-tooltip.hover.top title="Click to add this item to this outfit"></i>
                        </div>

                    </div>
                    <fashion-item ref="outputs"></fashion-item>
                </div>
            </div>
            <div v-show="isLoadingResult && isSubmitted">
                <base-alert type="primary">
                    <h1 class="text-secondary font-weight-bold mb-4" style="text-align:center">
                        Generating recommendations
                    </h1>
                    <base-progress type="success" :value="progress_val"></base-progress>
                </base-alert>
            </div>
        </div>
    </section>
</template>
<script>
    import FashionItem from "./FashionItem";


    const axios = require('axios');


    export default {
        components: {FashionItem},
        data() {
            return {
                isSubmitted: false,
                isLoadingResult: true,
                progress_val: 0
            }
        },
        methods: {
            generate: function () {
                let toSubmit = this.$refs.inputs.submit();
                console.log(toSubmit);
                console.log("sdfgdsgsdgdsg");
                if (toSubmit.item.length === 0) {
                    return;
                }
                this.progress_val = 0;
                this.isSubmitted = true;
                this.isLoadingResult = true;
                let self = this;
                axios.post('http://127.0.0.1:8000/predict/',
                    {
                        data: toSubmit
                    })
                    .then(function (response) {
                        // console.log(response);
                        let data = response.data;
                        let pred_cnt = data["pred_cnt"];
                        let recs = [];
                        for (let i = 0; i < pred_cnt; i++) {
                            // console.log("RESPONSE");
                            // console.log(data[i]);
                            recs = recs.concat(data[i])
                        }
                        self.$refs.outputs.isInput = false;
                        self.$refs.outputs.addRows(recs);
                        self.isLoadingResult = false;
                        self.progress_val = 0;
                    });
            },
            saveOutfit: function () {
                let allItems = this.$refs.inputs.getSelectedItems();
                if (this.isSubmitted) {
                    allItems = allItems.concat(this.$refs.outputs.getSelectedItems());
                }
                console.log(allItems);
                axios.post('http://127.0.0.1:8000/add_outfit/',
                    {
                        data: allItems
                    })
                    .then(function (response) {
                    });
            }
        },
        created() {
            let self = this;
            setInterval(function () {
                self.progress_val = (self.progress_val + 1) % 100;
            }, 100)
        }
    };
</script>
<style>
</style>
