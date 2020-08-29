<template>
    <div class="profile-page">
        <section class="section-profile-cover section-shaped my-0">
            <div class="shape shape-style-1 shape-primary shape-skew alpha-4">
                <span></span>
                <span></span>
                <span></span>
                <span></span>
                <span></span>
                <span></span>
                <span></span>
            </div>
        </section>
        <!--        <div class="col px-0">-->
        <!--            <section class="section section-skew">-->
        <!--                <div class="row justify-content-center align-items-center">-->
        <!--                    <div class="col-lg-7 text-center pt-lg">-->
        <!--                        <img src="../../../output/graph/color.png" height="1000" width="1000"/>-->
        <!--                    </div>-->
        <!--                </div>-->
        <!--            </section>-->
        <!--        </div>-->
        <div class="container shape-container d-flex">
            <section class="section section-skew">
                <div class="container">
                    <card shadow class="card-profile mt--300" no-body>
                        <div class="px-4">
                            <div class="row justify-content-center"
                                 v-on:click="img_id < img_max_id - 1 ? img_id += 1 : img_id = 0">
                                <div v-if="img_id === 0">
                                    <h2 class="h4 text-primary font-weight-bold mb-4">
                                        Item-item word embeddings
                                    </h2>
                                    <img src="../../../output/graph/item.png" height="900" width="900"/>
                                </div>
                                <div v-else-if="img_id === 1">
                                    <h2 class="h4 text-primary font-weight-bold mb-4">
                                        Color-color word embeddings
                                    </h2>
                                    <img src="../../../output/graph/color.png" height="900" width="900"/>
                                </div>
                                <div v-else-if="img_id === 2">
                                    <h2 class="h4 text-primary font-weight-bold mb-4">
                                        Item-color word embeddings
                                    </h2>
                                    <img src="../../../output/graph/item_color.png" height="900" width="900"/>
                                </div>
                                <div v-else-if="img_id === 3">
                                    <h2 class="h4 text-primary font-weight-bold mb-4">
                                        Item-material word embeddings
                                    </h2>
                                    <img src="../../../output/graph/item_material.png" height="900" width="900"/>
                                </div>
                                <div v-else-if="img_id === 4">
                                    <h2 class="h4 text-primary font-weight-bold mb-4">
                                        Material-color word embeddings
                                    </h2>
                                    <img src="../../../output/graph/material_color.png" height="900" width="900"/>
                                </div>
                                <div v-else-if="img_id === 5">
                                    <div class="row">
                                        <div class="col-md-12">
                                            <h2 class="text-primary font-weight-bold mb-4">User statistics</h2>
                                            <br>
                                            <h6 class="text-default font-weight-bold mb-4">
                                                Number of preferences: <strong>{{p_cnt}}</strong>
                                            </h6>
                                            <h6 class="text-default font-weight-bold mb-4">
                                                Number of outfits: <strong>{{o_cnt}}</strong>
                                            </h6>
                                            <h6 class="text-default font-weight-bold mb-4">
                                                Most picked item: <strong>{{top[0]}}</strong> with count <strong>{{top_cnt[0]}}</strong>
                                            </h6>
                                            <h6 class="text-default font-weight-bold mb-4">
                                                Most picked color: <strong>{{top[1]}}</strong> with count <strong>{{top_cnt[1]}}</strong>
                                            </h6>
                                            <h6 class="text-default font-weight-bold mb-4">
                                                Most picked material: <strong>{{top[2]}}</strong> with count <strong>{{top_cnt[2]}}</strong>
                                            </h6>
                                        </div>
                                    </div>

                                </div>
                            </div>
                        </div>
                    </card>
                </div>
            </section>
        </div>
    </div>
</template>
<script>
    const axios = require('axios');

    export default {
        data() {
            return {
                img_id: 0,
                img_max_id: 6,
                p_cnt: 0,
                o_cnt: 0,
                top: ["", "", ""],
                top_cnt: [0, 0, 0],
            }
        },

        created() {
            let self = this;
            axios.get('http://127.0.0.1:8000/get_user_summary/')
                .then(function (response) {
                    let summary = response.data["summary"];
                    self.p_cnt = summary["pref_cnt"];
                    self.o_cnt = summary["outfit_cnt"];
                    self.top = summary["top"];
                    self.top_cnt = summary["top_cnt"];
                    console.log(summary)
                });
        }
    };
</script>
<style>
</style>
