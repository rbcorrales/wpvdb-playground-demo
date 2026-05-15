<?php
/**
 * Demo plugin bootstrap.
 *
 * @package WPVDB_Playground_Demo
 */

namespace WPVDB_Playground_Demo;

defined( 'ABSPATH' ) || exit;

/**
 * Registers demo mode filters against core wpvdb.
 */
class Demo_Plugin {
	/**
	 * Admin helper.
	 *
	 * @var Demo_Admin|null
	 */
	private static $admin = null;

	/**
	 * Bootstrap once wpvdb has had a chance to load.
	 */
	public static function bootstrap() {
		if ( ! self::is_demo_mode() ) {
			return;
		}

		if ( ! self::wpvdb_is_compatible() ) {
			add_action( 'admin_notices', [ __CLASS__, 'dependency_notice' ] );
			return;
		}

		self::$admin = new Demo_Admin();

		add_filter( 'wpvdb_register_post_metabox', '__return_false' );
		add_filter( 'wpvdb_register_bulk_actions', '__return_false' );
		add_filter( 'wpvdb_render_bulk_embed_ui', '__return_false' );
		add_filter( 'wpvdb_render_test_embedding_ui', '__return_false' );
		add_filter( 'wpvdb_embeddings_search_enabled', '__return_false' );
		add_filter( 'wpvdb_query_accept_vector_field', '__return_true' );
		add_filter( 'wpvdb_render_editor_embedding_ui', '__return_false' );
		add_filter( 'wpvdb_render_dashboard_search_widget', '__return_false' );
		add_filter( 'wpvdb_render_status_tools_ui', '__return_false' );
		add_filter( 'wpvdb_enqueue_admin_script', '__return_false' );
		add_filter( 'wpvdb_log_to_error_log', '__return_false' );

		add_action( 'wpvdb_dashboard_widgets', [ self::$admin, 'render_preset_widget' ], 10 );
		add_action( 'admin_enqueue_scripts', [ self::$admin, 'enqueue_assets' ] );
	}

	/**
	 * Whether demo mode is enabled.
	 *
	 * @return bool
	 */
	public static function is_demo_mode() {
		return defined( 'WPVDB_PLAYGROUND_RUNTIME' ) && WPVDB_PLAYGROUND_RUNTIME
			&& defined( 'WPVDB_DEMO_MODE' ) && WPVDB_DEMO_MODE;
	}

	/**
	 * Whether the installed wpvdb exposes the hooks this plugin needs.
	 *
	 * @return bool
	 */
	private static function wpvdb_is_compatible() {
		if ( ! class_exists( '\WPVDB\Plugin' ) || ! defined( 'WPVDB_VERSION' ) ) {
			return false;
		}

		if ( ! defined( 'WPVDB_PLAYGROUND_SUPPORT_VERSION' ) ) {
			return false;
		}

		return version_compare( WPVDB_VERSION, WPVDB_PLAYGROUND_DEMO_MIN_WPVDB_VERSION, '>=' );
	}

	/**
	 * Explain missing or old wpvdb dependency.
	 */
	public static function dependency_notice() {
		if ( ! current_user_can( 'activate_plugins' ) ) {
			return;
		}

		$found = defined( 'WPVDB_VERSION' ) ? WPVDB_VERSION : __( 'not active', 'wpvdb-playground-demo' );
		?>
		<div class="notice notice-error">
				<p>
					<?php
					printf(
						/* translators: 1: minimum wpvdb version, 2: current wpvdb version or status. */
						esc_html__( 'WPVDB Playground Demo requires wpvdb %1$s or newer with Playground support hooks. Current wpvdb: %2$s.', 'wpvdb-playground-demo' ),
						esc_html( WPVDB_PLAYGROUND_DEMO_MIN_WPVDB_VERSION ),
						esc_html( $found )
					);
					?>
			</p>
		</div>
		<?php
	}
}
