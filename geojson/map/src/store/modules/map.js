//import shop from '../../api/shop'

import { resolveComponent } from "vue";

// initial state
const state = {
    url: "http://j-gimbel.ddns.net:8000", // "http://localhost:8000",
    LKID: null,
    geojson: "?"
}

// getters
const getters = {
    /*
    cartProducts: (state, getters, rootState) => {
      return state.items.map(({ id, quantity }) => {
        const product = rootState.products.all.find(product => product.id === id)
        return {
          title: product.title,
          price: product.price,
          quantity
        }
      })
    },
  
    cartTotalPrice: (state, getters) => {
      return getters.cartProducts.reduce((total, product) => {
        return total + product.price * product.quantity
      }, 0)
    }*/
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

        return fetch(state.url + "/api/landkreis/" + LKID, {
            mode: "cors",
        })
            .then((response) => response.json())
            .then(function (data) {
                console.log(data);

                commit('setLKID', LKID)
                commit('setLKData', data)

                //geojson.value = geojson_data;
                //geoJsonloaded.value = true;

                /*
                window.Plotly.newPlot(
                  document.getElementById("chart1"),
                  //date
                  [
                    {
                      x: [
                        "AG 0-4",
                        "AG 5-14",
                        "AG 15-34",
                        "AG 35-59",
                        "AG 60-79",
                        "AG 80+",
                      ],
                      y: [0, 1000, 0, 0, 0, 0],
                      type: "bar",
                    },
                  ],
                  //layout
                  { title: "Age groups distribution" },
                  //config
                  { responsive: true }
                );*/
            });
    }
    /*
    checkout({ commit, state }, products) {
        const savedCartItems = [...state.items]
        commit('setCheckoutStatus', null)
        // empty cart
        commit('setCartItems', { items: [] })
        shop.buyProducts(
            products,
            () => commit('setCheckoutStatus', 'successful'),
            () => {
                commit('setCheckoutStatus', 'failed')
                // rollback to the cart saved before sending the request
                commit('setCartItems', { items: savedCartItems })
            }
        )
    },
 
    addProductToCart({ state, commit }, product) {
        commit('setCheckoutStatus', null)
        if (product.inventory > 0) {
            const cartItem = state.items.find(item => item.id === product.id)
            if (!cartItem) {
                commit('pushProductToCart', { id: product.id })
            } else {
                commit('incrementItemQuantity', cartItem)
            }
            // remove 1 item from stock
            commit('products/decrementProductInventory', { id: product.id }, { root: true })
        }
    }*/
}

// mutations
const mutations = {

    setLKID(state, { id }) {
        state.LKID = id
    },
    setLKData(state, { data }) {
        state.LKData = data
    },


    setGeojson(state, geojson_data) {

        state.geojson = geojson_data

    },



    /*
    pushProductToCart(state, { id }) {
        state.items.push({
            id,
            quantity: 1
        })
    },
 
    incrementItemQuantity(state, { id }) {
        const cartItem = state.items.find(item => item.id === id)
        cartItem.quantity++
    },
 
    setCartItems(state, { items }) {
        state.items = items
    },
 
    setCheckoutStatus(state, status) {
        state.checkoutStatus = status
    }*/
}

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
}