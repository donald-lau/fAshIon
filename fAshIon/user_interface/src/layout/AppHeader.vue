<template>
    <header class="header-global">
        <base-nav class="navbar-main" transparent type="" effect="light" expand>
            <router-link slot="brand" class="mr-lg-5" to="/">
                <h1 style="color:floralwhite; display: inline" class="display-2"><strong>f</strong></h1>
                <h1 style="color:floralwhite; display: inline" class="display-1"><strong>A</strong></h1>
                <h1 style="color:floralwhite; display: inline" class="display-2"><strong>sh</strong></h1>
                <h1 style="color:floralwhite; display: inline" class="display-1"><strong>I</strong></h1>
                <h1 style="color:floralwhite; display: inline" class="display-2"><strong>on</strong></h1>
            </router-link>

            <div class="row" slot="content-header" slot-scope="{closeMenu}">
                <div class="col-6 collapse-brand">
                    <a href="https://demos.creative-tim.com/vue-argon-design-system/documentation/">
                        <h1 class="display-2"><strong>fAshIon</strong></h1>
                    </a>
                </div>
                <div class="col-6 collapse-close">
                    <close-button @click="closeMenu"></close-button>
                </div>
            </div>

            <ul class="navbar-nav navbar-nav-hover align-items-lg-center">
                <router-link to="/" slot="title" href="#" class="nav-link" role="button">
                    <i class="ni ni-active-40 d-lg-none"></i>
                    <span class="nav-link-inner--text">Use Magic</span>
                </router-link>
                <router-link to="/landing" slot="title" href="#" class="nav-link" role="button">
                    <i class="ni ni-favourite-28 d-lg-none"></i>
                    <span class="nav-link-inner--text">Past Selections</span>
                </router-link>
                <router-link to="/profile" slot="title" href="#" class="nav-link" role="button">
                    <i class="ni ni-atom d-lg-none"></i>
                    <span class="nav-link-inner--text">Statistics</span>
                </router-link>
            </ul>
            <ul class="navbar-nav align-items-lg-center ml-lg-auto">
                <!--                <li class="nav-item d-none d-lg-block ml-lg-4">-->
                <!--                    <a href="" rel="noopener" class="btn btn-neutral btn-icon">-->
                <!--                <span class="btn-inner&#45;&#45;icon">-->
                <!--                  <i class="fa fa-user mr-2"></i>-->
                <!--                </span>-->
                <!--                        <span class="nav-link-inner&#45;&#45;text">User</span>-->
                <!--                    </a>-->
                <!--                </li>-->
                <base-dropdown>
                    <base-button slot="title" type="secondary" class="dropdown-toggle">
                        {{current_user}}
                    </base-button>
                    <div v-for="(name, index) in user_display_name">
                        <div class="dropdown-item" v-on:click="setUser(name)">{{name}}</div>
                    </div>
<!--                    <div class="dropdown-item" v-on:click="setUser('Default', 'Default User')">Default User</div>-->
<!--                    <div class="dropdown-item" v-on:click="setUser('user_1', 'John')">User 1</div>-->
<!--                    <div class="dropdown-item" v-on:click="setUser('user_2', 'Mary')">User 2</div>-->
                </base-dropdown>
            </ul>
        </base-nav>
    </header>
</template>
<script>
    import BaseNav from "@/components/BaseNav";
    import BaseDropdown from "@/components/BaseDropdown";
    import CloseButton from "@/components/CloseButton";

    const axios = require('axios');

    export default {
        data() {
            return {
                current_user: "Default",
                user_display_name: [
                    "Default",
                    "Adam(Black)",
                    "Beverly(BlackAndWhite)",
                    "Charles(Red)",
                    "Danielle(Navy)",
                    "Eden(Green)",
                    "Frank(Formal)",
                    "Gigi(SemiFormal)",
                    "Helen(Casual)",
                    "Ivan(Sporty)",
                    "Jen(CasualInBlack)"
                ],
            }
        },
        components: {
            BaseNav,
            CloseButton,
            BaseDropdown
        },
        methods: {
            setUser: function (user_public_name) {
                this.current_user = user_public_name;
                let uid = user_public_name.toLowerCase();
                uid += "_" + this.user_display_name.indexOf(user_public_name);
                console.log(uid);
                let self = this;
                axios.post('http://127.0.0.1:8000/set_user/',
                    {
                        user_id: uid,
                    })
                    .then(function (response) {
                        self.$forceUpdate();
                        self.$router.push("/");
                    });
            }
        }
    };
</script>
<style>
</style>
