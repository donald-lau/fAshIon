<!--            <div item="col-md-4">-->
<!--                <div item="form-group">-->
<!--                    <input type="text" placeholder="Color" item="form-control"  v-model="line.countryCode"/>-->
<!--                </div>-->
<!--            </div>-->

<template>
    <div id="app-input">
        <div v-for="(row, index) in rows">
            <br>
            <div class="row">
                <div class="col-md-5">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="form-group" v-on:click="setFocusRow(row)">
                                <!--                                <input type="text" placeholder="Color" class="form-control"-->
                                <!--                                    v-model="row.color" v-on:focus="setFocusRow(row)"/>-->
                                <vue-single-select
                                        placeholder=""
                                        v-model="row.color"
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
                            <div class="form-group" v-on:click="setFocusRow(row)">
                                <!--                                <input type="text" placeholder="Material" class="form-control"-->
                                <!--                                       v-model="row.material" v-on:focus="setFocusRow(row)"/>-->
                                <vue-single-select
                                        placeholder=""
                                        v-model="row.material"
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
                    <div class="form-group" v-on:click="setFocusRow(row)">
                        <!--                        <input type="text" placeholder="Fashion item" class="form-control"-->
                        <!--                               v-model="row.item" v-on:focus="setFocusRow(row)"/>-->
                        <vue-single-select
                                placeholder=""
                                v-model="row.item"
                                :options="allItems"
                                :max-results="100"
                                :classes="{input: 'form-control ', dropdown: 'dropdown'}"
                        ></vue-single-select>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="form-group">
                        <div v-model="row.image"></div>
                        <img style="max-width: 100%" v-bind:src="row.urls[row.url_id]"
                             v-on:click="row.url_id < row.url_max_id - 1 ? row.url_id += 1 : row.url_id = 0"/>
                    </div>
                </div>
                <div class="col-md-1" v-show="isInput"></div>
                <div class="col-md-1" v-show="!isInput">
                    <button v-bind:class="[selected[index] ? btnDel : btnAdd]" type="button"
                            v-on:click="toggleSaved(index)"
                            style="cursor: pointer">
                        <span class="btn-inner--icon"><i
                                v-bind:class="[selected[index] ? iconDel : iconAdd]"></i></span>
                    </button>
                </div>
                <div class="col-md-1">
                    <button class="btn btn-icon btn-2 btn-primary" type="button"
                            v-if="!isInput || rows.length > 1" v-on:click="removeElement(index)"
                            style="cursor: pointer">
                        <span class="btn-inner--icon"><i class="ni ni-fat-remove"></i></span>
                    </button>
                </div>
            </div>
            <div v-if="!isInput">
                <div class="row">
                    <div class="col-md-8">Explanations  <i class="fa fa-question-circle"
                       v-b-tooltip.hover.top title="sim-comp value stands for similarity/compatibility value"></i></div>
                    <div class="col-md-2"><i>Rating (%)</i></div>
                    <div class="col-md-2"><i>Send feedback</i></div>
                </div>
                <div v-for="(reason, idx) in row.reasons">
                    <div class="row">
                        <div class="col-md-8"><strong>{{reason.type}}</strong>: {{reason.displayText}}</div>
                        <div class="col-md-2">
                            <input type="text" class="form-control"
                                   v-model="reason.displayRating"
                                   :placeholder="reason.displayRating">
                        </div>
                        <div class="col-md-2">
                            <button class="btn btn-icon btn-2 btn-outline-dark" type="button"
                                    v-on:click="updatePref(reason)">
                                <span class="btn-inner--icon"><i class="fa fa-level-up"></i></span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <hr>
        </div>
        <div v-if="isInput">
            <button type="button" class="btn btn-primary" v-on:click="addRows()">New item</button>
        </div>
    </div>
</template>

<script>
    import debounce from 'debounce'

    const axios = require('axios');

    export default {
        name: 'FashionItem',
        data() {
            return {
                // for form input
                rows: [],
                selected: [],
                focusRow: null,
                isInput: true,

                // for autocomplete
                allColors: [],
                allMaterials: [],
                allItems: [],

                // for UI
                btnAdd: "btn btn-icon btn-2 btn-info",
                iconAdd: "ni ni-fat-add",
                btnDel: "btn btn-icon btn-2 btn-warning",
                iconDel: "ni ni-fat-delete",
            }
        },
        methods: {
            addRows: function (recs) {
                // phrase recommendations
                if (recs) {
                    if (!this.isInput) {
                        this.rows = [];
                        this.selected = [];
                    }
                    for (let i = 0; i < recs.length; i++) {
                        // TODO: user input validation
                        let data = recs[i];
                        let rec = {
                            color: data["color"]["color"],
                            item: data["item"]["item"],
                            material: data["material"]["material"],
                            image: "",
                            urls: data["urls"],
                            url_id: 0,
                            url_max_id: data["url_max_id"]
                        };

                        function phraseReasoning(reason) {
                            let displayText = reason["onto_0"] + " has a sim-comp value " + reason["value"].toFixed(6);
                            displayText = reason["onto_1"] === "" ? displayText :
                                displayText + " pairing " + reason["onto_1"];
                            displayText = reason["modifier"] === 1 ? displayText :
                                displayText + " with a user rating of " + String(reason["modifier"] * 100) + "%";
                            reason["displayText"] = displayText;
                            reason["displayRating"] = String(reason["modifier"] * 100);
                            return reason;
                        }

                        let reasons = data["item"]["reason"];
                        reasons = reasons.concat(data["material"]["reason"]);
                        reasons = reasons.concat(data["color"]["reason"]);
                        reasons = reasons.map(x => phraseReasoning(x));
                        rec["reasons"] = reasons;
                        console.log(rec);
                        this.rows.push(rec);
                    }
                    //  add new rows for user input
                } else {
                    this.rows.push({
                        color: "",
                        item: "",
                        material: "",
                        image: "",
                        urls: [],
                        url_id: 0,
                        url_max_id: 0
                    });
                }

            },
            removeElement: function (index) {
                this.rows.splice(index, 1);

            },
            getImageUrl: function (row, previousRowImage) {
                if (row.item !== "" && row.item !== null) {
                    row.image = "";
                    if (row.color !== "" || row.color !== null) {
                        row.image += row.color + " ";
                    }
                    if (row.material !== "" || row.material !== null) {
                        row.image += row.material + " ";
                    }
                    row.image += row.item;
                    if (previousRowImage !== row.image) {
                        axios.post('http://127.0.0.1:8000/image_search/',
                            {
                                search: row.image,
                                color: row.color,
                                material: row.material,
                                item: row.item
                            })
                            .then(function (response) {
                                for (var key in response.data) break;
                                let urls = response.data[key];
                                row.url_max_id = urls.length;
                                row.urls = urls;
                            });
                    }
                    return row.image
                }

            },
            setFocusRow: function (row) {
                this.focusRow = row
            },
            submit: function () {
                let inputs = {
                    color: [],
                    item: [],
                    material: [],
                    url: []
                };
                for (let i = 0; i < this.rows.length; i++) {
                    if (this.rows[i].item === null) {
                        break;
                    }
                    inputs.color.push(this.rows[i].color === null ? "" : this.rows[i].color);
                    inputs.item.push(this.rows[i].item);
                    inputs.material.push(this.rows[i].material === null ? "" : this.rows[i].material);
                    inputs.url.push(this.rows[i].urls[this.rows[i].url_id]);
                }
                return inputs
            },
            setRows: function (rows) {
                this.rows = rows;
                if (!this.isInput) {
                    this.selected = [];
                    for (let i = 0; i < rows.length; i++) {
                        this.selected.push(false);
                    }

                }
            },
            updatePref: function (reason) {
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
                    });
            },
            toggleSaved: function (index) {
                this.selected[index] = !this.selected[index];
                // console.log(this.selected);
                this.$forceUpdate();
            },
            getSelectedItems: function () {
                if (this.isInput) {
                    return this.rows
                } else {
                    let ret = [];
                    for (let i = 0; i < this.selected.length; i++) {
                        if (this.selected[i]) {
                            ret.push(this.rows[i])
                        }
                    }
                    return ret
                }
            }
        },
        watch: {
            focusRow: {
                deep: true,
                lastSearch: "some random init value",
                handler(focusRow) {
                    this.lastSearch = this.getImageUrl(focusRow, this.lastSearch);
                }
            }
        },
        created() {
            if (this.isInput) {
                this.addRows();
            }
            this.getImageUrl = debounce(this.getImageUrl, 600);
            let self = this;
            axios.get('http://127.0.0.1:8000/get_onto_vocabs/')
                .then(function (response) {
                    self.allColors = response.data["allColors"].sort();
                    self.allMaterials = response.data["allMaterials"].sort();
                    self.allItems = response.data["allItems"].sort();
                    // self.$forceUpdate();
                });
        }
    }
</script>