import { createStore, createLogger } from 'vuex'
import map from './modules/map'
//import products from './modules/products'

const debug = process.env.NODE_ENV !== 'production'

export default createStore({
    modules: {
        //cart,
        //products
        map
    },
    strict: debug,
    plugins: debug ? [createLogger()] : []
})