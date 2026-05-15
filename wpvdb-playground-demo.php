<?php
/**
 * Plugin Name:       WPVDB Playground Demo
 * Plugin URI:        https://github.com/rbcorrales/wpvdb-playground-demo
 * Description:       Demo packaging for running wpvdb inside WordPress Playground.
 * Version:           0.1.0
 * Author:            Automattic, Ramon Corrales
 * Author URI:        https://automattic.com/
 * Requires at least: 6.5
 * Requires PHP:      7.4
 * Requires Plugins:  wpvdb
 * License:           GPL-2.0-or-later
 * License URI:       https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain:       wpvdb-playground-demo
 * Domain Path:       /languages
 *
 * @package WPVDB_Playground_Demo
 */

defined( 'ABSPATH' ) || exit;

define( 'WPVDB_PLAYGROUND_DEMO_VERSION', '0.1.0' );
define( 'WPVDB_PLAYGROUND_DEMO_MIN_WPVDB_VERSION', '1.0.16' );
define( 'WPVDB_PLAYGROUND_DEMO_FILE', __FILE__ );
define( 'WPVDB_PLAYGROUND_DEMO_DIR', plugin_dir_path( __FILE__ ) );
define( 'WPVDB_PLAYGROUND_DEMO_URL', plugin_dir_url( __FILE__ ) );

require_once WPVDB_PLAYGROUND_DEMO_DIR . 'includes/class-demo-admin.php';
require_once WPVDB_PLAYGROUND_DEMO_DIR . 'includes/class-demo-plugin.php';

add_action( 'plugins_loaded', [ \WPVDB_Playground_Demo\Demo_Plugin::class, 'bootstrap' ], 20 );
