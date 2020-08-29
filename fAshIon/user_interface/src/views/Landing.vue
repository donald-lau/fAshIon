<template>
    <div>

        <div class="position-relative">
            <!-- shape Hero -->
            <section class="section-shaped my-0">
                <div class="shape shape-style-1 shape-default shape-skew">
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <div class="container shape-container d-flex">
                    <div class="col px-0">
                        <div>
                            <base-alert type="secondary">
                                <h2 class="h4 text-primary font-weight-bold mb-4">
                                    Your personal preferences
                                </h2>
                                <!--                                <strong>Passive</strong>: heels has a modifier value of 0.42-->
                                <div class="row">
                                    <div class="col-md-8"><strong>Prefer</strong></div>
                                    <div class="col-md-2"><strong>Rating</strong></div>
                                    <div class="col-md-1"><strong>Save</strong></div>
                                    <div class="col-md-1"><strong>Remove</strong></div>
                                </div>
                                <div v-for="(reason, idx) in reasons">
                                    <div class="row">
                                        <div class="col-md-8"
                                             style="display: flex; align-items: center; justify-content: left;">
                                            <strong>{{reason.type}}</strong>: {{reason.displayText}}
                                        </div>
                                        <div class="col-md-2">
                                            <input type="text" class="form-control"
                                                   v-model="reason.displayRating"
                                                   :placeholder="reason.displayRating">
                                        </div>
                                        <div class="col-md-1">
                                            <button class="btn btn-icon btn-2 btn-outline-primary" type="button"
                                                    v-on:click="updatePref(reason)">
                                                <span class="btn-inner--icon"><i class="fa fa-save"></i></span>
                                            </button>
                                        </div>
                                        <div class="col-md-1">
                                            <button class="btn btn-icon btn-2 btn-outline-warning" type="button"
                                                    v-on:click="removePref(reason)">
                                                <span class="btn-inner--icon"><i class="fa fa-trash"></i></span>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </base-alert>
                        </div>
                        <hr>

                        <div>
                            <base-alert type="secondary">
                                <h2 class="h4 text-primary font-weight-bold mb-4">
                                    Your saved outfits
                                </h2>
                                <hr>
                                <div v-for="(outfit, idx) in outfits">
                                    <div class="row">
                                        <div class="col-md-11">
                                            <h4>Outfit {{idx + 1}}</h4>
                                        </div>
                                        <div class="col-md-1">
                                            <button class="btn btn-icon btn-2 btn-danger" type="button"
                                                    v-on:click="removeOutfit(outfit)">
                                                <span class="btn-inner--icon"><i class="fa fa-trash"></i></span>
                                            </button>
                                        </div>
                                    </div>
                                    <br>
                                    <div v-for="(item, itemId) in outfit.item">
                                        <!--                                        <h5>{{outfit.color[itemId]}} {{outfit.material[itemId]}} {{item}}</h5>-->
                                        <div class="row">
                                            <div class="col-md-5">
                                                <div class="row">
                                                    <div class="col-md-6">
                                                        <div class="form-group" v-on:click="setFocus(outfit, itemId)">
                                                            <!--                                <input type="text" placeholder="Color" class="form-control"-->
                                                            <!--                                    v-model="row.color" v-on:focus="setFocusRow(row)"/>-->
                                                            <vue-single-select
                                                                    :placeholder="outfit.color[itemId]"
                                                                    v-model="outfit.color[itemId]"
                                                                    :options="allColors"
                                                                    :max-results="100"
                                                                    :classes="{
                                                                    input: 'form-control ',
                                                                    dropdown: 'dropdown'
                                                                }"
                                                            ></vue-single-select>
                                                        </div>
                                                    </div>
                                                    <div class="col-md-6">
                                                        <div class="form-group" v-on:click="setFocus(outfit, itemId)">
                                                            <!--                                <input type="text" placeholder="Material" class="form-control"-->
                                                            <!--                                       v-model="row.material" v-on:focus="setFocusRow(row)"/>-->
                                                            <vue-single-select
                                                                    :placeholder="outfit.material[itemId]"
                                                                    v-model="outfit.material[itemId]"
                                                                    :options="allMaterials"
                                                                    :max-results="100"
                                                                    :classes="{
                                                                    input: 'form-control ',
                                                                    dropdown: 'dropdown'
                                                                }"
                                                            ></vue-single-select>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="col-md-3">
                                                <div class="form-group" v-on:click="setFocus(outfit, itemId)">
                                                    <!--                        <input type="text" placeholder="Fashion item" class="form-control"-->
                                                    <!--                               v-model="row.item" v-on:focus="setFocusRow(row)"/>-->
                                                    <vue-single-select
                                                            :placeholder="outfit.item[itemId]"
                                                            v-model="outfit.item[itemId]"
                                                            :options="allItems"
                                                            :max-results="100"
                                                            :classes="{input: 'form-control ', dropdown: 'dropdown'}"
                                                    ></vue-single-select>
                                                </div>
                                            </div>
                                            <div class="col-md-2">
                                                <div class="form-group">
                                                    <img style="max-width: 100%"
                                                         v-bind:src="outfit.image[itemId][outfit.imgId[itemId]]"
                                                         v-on:click="updateDisplayImg(outfit, itemId)"/>
                                                </div>
                                            </div>
                                            <div class="col-md-1">
                                                <button class="btn btn-icon btn-2 btn-outline-primary" type="button"
                                                        v-on:click="updateItem(outfit, itemId)">
                                                    <span class="btn-inner--icon"><i class="fa fa-save"></i></span>
                                                </button>
                                            </div>
                                            <div class="col-md-1">
                                                <button class="btn btn-icon btn-2 btn-outline-warning" type="button"
                                                        v-on:click="removeItem(outfit, itemId)">
                                                    <span class="btn-inner--icon"><i class="fa fa-trash"></i></span>
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                    <hr>
                                </div>
                                <!--                                <strong>Passive</strong>: heels has a modifier value of 0.42-->
                            </base-alert>
                        </div>
                        <hr>
                    </div>
                </div>
            </section>
        </div>
    </div>
</template>

<script>
    import FashionItem from "./components/FashionItem";
    import debounce from 'debounce'

    const axios = require('axios');

    export default {
        name: "home",
        components: {FashionItem},
        data() {
            return {
                reasons: [{type: "", displayText: "", displayRating: ""}],
                outfits: [],
                // for autocomplete
                allColors: [],
                allMaterials: [],
                allItems: [],
                focus: null,
            }
        },
        methods: {
            phraseReasoning: function (reason) {
                let displayText = reason["onto_0"] + " has a sim-comp value " + reason["value"].toFixed(6);
                displayText = reason["onto_1"] === "" ? displayText :
                    displayText + " pairing " + reason["onto_1"];
                displayText = reason["modifier"] === 1 ? displayText :
                    displayText + " with a rating of " + String(reason["modifier"] * 100).substring(0, 6) + "%";
                reason["displayText"] = displayText;
                reason["displayRating"] = String(reason["modifier"] * 100).substring(0, 6);
                return reason;
            },
            updatePref: function (reason) {
                let self = this;
                let pref = {
                    "type": 1,
                    "value": reason["value"],
                    "modifier": parseFloat(reason["displayRating"]) / 100,
                    "onto_0": reason["onto_0"],
                    "onto_1": reason["onto_1"]
                };
                axios.post('http://127.0.0.1:8000/update_pref/',
                    {
                        data: pref
                    })
                    .then(function (response) {
                        axios.get('http://127.0.0.1:8000/get_user_pref/')
                            .then(function (response) {
                                let reasons = response.data["pref"];
                                self.reasons = reasons.map(x => self.phraseReasoning(x));
                            });
                        self.$forceUpdate();
                    });
            },
            removePref: function (reason) {
                let self = this;
                axios.post('http://127.0.0.1:8000/del_user_pref_outfit/',
                    {
                        data: reason.id,
                        type: "pref"
                    })
                    .then(function (response) {
                        axios.get('http://127.0.0.1:8000/get_user_pref/')
                            .then(function (response) {
                                let reasons = response.data["pref"];
                                self.reasons = reasons.map(x => self.phraseReasoning(x));
                            });
                        self.$forceUpdate();
                    });
            },
            removeOutfit: function (outfit) {
                let self = this;
                axios.post('http://127.0.0.1:8000/del_user_pref_outfit/',
                    {
                        data: outfit.id,
                        type: "outfit"
                    })
                    .then(function (response) {
                        axios.get('http://127.0.0.1:8000/get_user_outfit/')
                            .then(function (response) {
                                self.outfits = response.data["outfit"];
                                for (let i = 0; i < self.outfits.length; i++) {
                                    self.outfits[i].imgId = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
                                }
                                self.$forceUpdate();
                            });
                        self.$forceUpdate();
                    });
            },
            removeItem: function (outfit, itemRowId) {
                let self = this;
                let imgId = outfit.imgId;
                axios.post('http://127.0.0.1:8000/delete_item_in_outfit/',
                    {
                        data: itemRowId,
                        outfitId: outfit.id
                    })
                    .then(function (response) {
                        axios.get('http://127.0.0.1:8000/get_user_outfit/')
                            .then(function (response) {
                                self.outfits = response.data["outfit"];
                                for (let i = 0; i < self.outfits.length; i++) {
                                    self.outfits[i].imgId = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
                                }
                                self.$forceUpdate();
                            });
                        self.$forceUpdate();
                    });
            },
            updateItem: function (outfit, itemRowId) {
                let self = this;
                console.log(outfit);
                axios.post('http://127.0.0.1:8000/update_outfit/',
                    {
                        data: itemRowId,
                        outfitId: outfit.id,
                        item: outfit.item[itemRowId],
                        color: outfit.color[itemRowId],
                        material: outfit.material[itemRowId],
                        image: outfit.image[itemRowId][outfit.imgId[itemRowId]]
                    })
                    .then(function (response) {
                        axios.get('http://127.0.0.1:8000/get_user_outfit/')
                            .then(function (response) {
                                self.outfits = response.data["outfit"];
                                for (let i = 0; i < self.outfits.length; i++) {
                                    self.outfits[i].imgId = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
                                }
                                self.$forceUpdate();
                            });
                        self.$forceUpdate();
                    });
            },
            setFocus: function (outfit, rowId) {
                this.focus = {outfit: outfit, rowId: rowId};
            },
            updateDisplayImg: function (outfit, itemId) {
                outfit.imgId[itemId] + 1 < outfit.image[itemId].length ?
                    outfit.imgId[itemId] += 1 : outfit.imgId[itemId] = 0;
                this.$forceUpdate();
            },
            getImageUrl: function (focus, prevFocus) {
                console.log("get image");
                let outfit = focus.outfit;
                let rowId = focus.rowId;
                if (outfit.item[rowId] !== "" && outfit.item[rowId] !== null) {
                    let thisSearch = "";
                    if (outfit.color[rowId] !== "" || outfit.color[rowId] !== null) {
                        thisSearch += outfit.color[rowId] + " ";
                    }
                    if (outfit.material[rowId] !== "" || outfit.material[rowId] !== null) {
                        thisSearch += outfit.material[rowId] + " ";
                    }
                    thisSearch += outfit.item[rowId];
                    if (thisSearch !== prevFocus) {
                        console.log({
                            search: thisSearch,
                        });
                        let self = this;
                        axios.post('http://127.0.0.1:8000/new_image_for_outfit/',
                            {
                                search: thisSearch,
                                color: outfit.color[rowId],
                                material: outfit.material[rowId],
                                item: outfit.item[rowId]
                            })
                            .then(function (response) {
                                let urls = response.data["urls"];
                                for (let i = 0; i < self.outfits.length; i++) {
                                    if (self.outfits[i].id === outfit.id) {
                                        self.outfits[i].image[rowId] = urls;
                                        break;
                                    }
                                }
                                self.$forceUpdate();
                            });
                    }
                    console.log("done get image");
                    return thisSearch
                }

            },

        },
        watch: {
            focus: {
                deep: true,
                lastFocus: "some random init value",
                handler(focus) {
                    this.lastFocus = this.getImageUrl(focus, this.lastFocus);
                }
            }
        },
        created() {
            let self = this;
            axios.get('http://127.0.0.1:8000/get_user_pref/')
                .then(function (response) {
                    let reasons = response.data["pref"];
                    self.reasons = reasons.map(x => self.phraseReasoning(x));
                    self.$forceUpdate();
                });
            axios.get('http://127.0.0.1:8000/get_user_outfit/')
                .then(function (response) {
                    let outfits = response.data["outfit"];
                    self.outfits = outfits;
                    for (let i = 0; i < self.outfits.length; i++) {
                        self.outfits[i].imgId = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    }
                    self.$forceUpdate();
                });
            axios.get('http://127.0.0.1:8000/get_onto_vocabs/')
                .then(function (response) {
                    self.allColors = response.data["allColors"].sort();
                    self.allMaterials = response.data["allMaterials"].sort();
                    self.allItems = response.data["allItems"].sort();
                    self.$forceUpdate();
                });
            this.getImageUrl = debounce(this.getImageUrl, 600);

        }
    };
</script>
