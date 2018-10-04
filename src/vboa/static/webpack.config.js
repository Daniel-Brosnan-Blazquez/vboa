const webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');

const config = {
    entry:  __dirname + '/js/vboa.js',
    output: {
        path: __dirname + '/dist',
        filename: 'bundle.js',
    },
    resolve: {
        extensions: [".js", ".css"]
    },
    module: {
        rules: [
            {
                test: /\.js?/,
                exclude: /node_modules/,
                use: 'babel-loader'
            },
            {
                test: /\.css$/,
                use: ExtractTextPlugin.extract({
                    fallback: 'style-loader',
                    use: 'css-loader',
                })
            },
            {
                test: /\.(png|svg|jpg|gif|ttf|woff2|woff|eot)$/,
                use: 'file-loader'
            }
        ]
    },
    plugins: [
        new ExtractTextPlugin('styles.css'),
        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery"
        })
    ]

};

module.exports = config;

