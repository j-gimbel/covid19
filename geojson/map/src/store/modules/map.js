import { resolveComponent } from "vue";

// initial state
const state = {
    url: "http://j-gimbel.ddns.net:8000",
    //url: "http://localhost:8000",
    //geojson: "?",
    LKID: null,
    LKName: "",
    BRData: null,
    LKData: null,
    LKDataDetails: null,
    LKIncidence: null
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


    },

    async loadLKDataDetails({ commit, state }, LKID) {

        return new Promise((resolve, reject) => {
            var url = new URL(state.url + "/api/landkreis/" + LKID + "/timeline"),
                params = { lat: 35.696233, long: 139.570431 }
            url.searchParams.append("params", JSON.stringify(["incidence"]))
            fetch(url, {
                mode: "cors",
            })
                .then((response) => response.json())
                .then(function (data) {
                    console.log(data);

                    commit('setLKDataDetails', data)
                    resolve(data)
                });
        })


    },

    async loadBRData({ commit, state }) {
        return new Promise((resolve, reject) => {

            if (state.BRData == null) {
                fetch(state.url + "/api/bundesrepublik", {
                    mode: "cors",
                })
                    .then((response) => response.json())
                    .then(function (BRData) {
                        console.log(BRData);
                        commit('setBRData', BRData)
                        resolve(true)
                    });
            }
            else {
                resolve(true)
            }
        })

    }

}

// mutations
const mutations = {

    setLKID(state, id) {
        state.LKID = id
    },
    setBRData(state, data) {
        console.log("setBRData", data)
        state.BRData = data
    },
    setLKData(state, data) {
        console.log("setLKData", data)
        state.LKData = data
    },

    setLKDataDetails(state, data) {
        console.log("setLKDataDetails", data)
        state.LKDataDetails = data
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