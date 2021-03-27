//import shop from '../../api/shop'

import { resolveComponent } from "vue";

// initial state
const state = {
    url: "http://j-gimbel.ddns.net:8000", // "http://localhost:8000",
    //geojson: "?",
    LKID: null,
    LKName: "Moop",
    LKData: "aaaaa"
}

// getters
const getters = {

}

// actions
const actions = {

    async getGeojson({ commit, state }) {
        console.log("getGeojson")
        var myHeaders = new Headers();
        myHeaders.append("pragma", "no-cache");
        myHeaders.append("cache-control", "no-cache");
        myHeaders.append("Content-Type", "application/json");
        myHeaders.append("Accept", "application/json");
        var myInit = {
            method: "GET",
            headers: myHeaders,
        };

        var myRequest = new Request("landkreise_rki.geojson");
        return new Promise((resolve) => {
            fetch(myRequest, myInit)
                .then((response) => response.json())
                .then(function (geojson_data) {
                    console.log(geojson_data);
                    commit('setGeojson', geojson_data)
                    resolve(geojson_data)
                });
        })


    },


    async loadLKData({ commit, state }, LKID) {

        return new Promise((resolve, reject) => {
            fetch(state.url + "/api/landkreis/" + LKID, {
                mode: "cors",
            })
                .then((response) => response.json())
                .then(function (LKData) {
                    console.log(LKData);

                    commit('setLKID', LKID)
                    commit('setLKData', LKData)
                    resolve(LKData)
                });
        })
    }

}

// mutations
const mutations = {

    setLKID(state, id) {
        state.LKID = id
    },
    setLKData(state, data) {
        console.log("setLKData", data)
        state.LKData = data
    },

    setHoveredLKName(state, LKName) {
        console.log("setHoveredLKName", LKName)
        state.LKName = LKName

    }


}

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
}