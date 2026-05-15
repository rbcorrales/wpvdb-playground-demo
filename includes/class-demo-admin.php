<?php
/**
 * Demo admin UI.
 *
 * @package WPVDB_Playground_Demo
 */

namespace WPVDB_Playground_Demo;

defined( 'ABSPATH' ) || exit;

/**
 * Renders and powers the Playground demo dashboard panel.
 */
class Demo_Admin {
	/**
	 * Read and normalize preset query vectors.
	 *
	 * @return array<int, array{id: string, label: string, vector: array<int, float>}>
	 */
	public static function get_presets() {
		$raw = get_option( 'wpvdb_demo_preset_queries', [] );
		if ( ! is_array( $raw ) ) {
			return [];
		}

		$dim = defined( 'WPVDB_DEFAULT_EMBED_DIM' ) ? (int) WPVDB_DEFAULT_EMBED_DIM : 0;
		if ( $dim < 1 ) {
			return [];
		}

		$out = [];
		foreach ( $raw as $entry ) {
			if ( ! is_array( $entry ) ) {
				continue;
			}

			$id     = isset( $entry['id'] ) ? (string) $entry['id'] : '';
			$label  = isset( $entry['label'] ) ? (string) $entry['label'] : '';
			$vector = isset( $entry['vector'] ) && is_array( $entry['vector'] ) ? $entry['vector'] : null;
			if ( '' === $id || '' === $label || ! is_array( $vector ) || count( $vector ) !== $dim ) {
				continue;
			}

			$clean = [];
			$bad   = false;
			foreach ( $vector as $value ) {
				if ( ! is_numeric( $value ) ) {
					$bad = true;
					break;
				}

				$float = (float) $value;
				if ( ! is_finite( $float ) ) {
					$bad = true;
					break;
				}

				$clean[] = $float;
			}

			if ( $bad ) {
				continue;
			}

			$out[] = [
				'id'     => $id,
				'label'  => $label,
				'vector' => $clean,
			];
		}

		return $out;
	}

	/**
	 * Map demo embedding document ids to post display metadata.
	 *
	 * @return array<int, array{title: string, permalink: string}>
	 */
	public static function get_posts_by_doc_id() {
		global $wpdb;

		$model = 'wpvdb-demo-' . ( defined( 'WPVDB_DEFAULT_EMBED_DIM' ) ? (int) WPVDB_DEFAULT_EMBED_DIM : 0 );
		$table = esc_sql( $wpdb->prefix . 'wpvdb_embeddings' );
		// phpcs:ignore WordPress.DB.PreparedSQL.InterpolatedNotPrepared, WordPress.DB.DirectDatabaseQuery.DirectQuery, WordPress.DB.DirectDatabaseQuery.NoCaching -- Table name is built from the trusted WordPress prefix and used for local demo metadata.
		$ids = $wpdb->get_col( $wpdb->prepare( "SELECT DISTINCT doc_id FROM {$table} WHERE model = %s", $model ) );
		if ( empty( $ids ) ) {
			return [];
		}

		$out = [];
		foreach ( $ids as $doc_id ) {
			$post_id = (int) $doc_id;
			$post    = get_post( $post_id );
			if ( ! $post || 'publish' !== $post->post_status ) {
				continue;
			}

			$out[ $post_id ] = [
				'title'     => get_the_title( $post ),
				'permalink' => esc_url_raw( get_permalink( $post ) ? get_permalink( $post ) : '' ),
			];
		}

		return $out;
	}

	/**
	 * Enqueue the dashboard demo script.
	 *
	 * @param string $hook Admin screen hook.
	 */
	public function enqueue_assets( $hook ) {
		if ( ! Demo_Plugin::is_demo_mode() || 'toplevel_page_wpvdb-dashboard' !== $hook ) {
			return;
		}

		wp_enqueue_script(
			'wpvdb-playground-demo',
			WPVDB_PLAYGROUND_DEMO_URL . 'assets/js/wpvdb-demo.js',
			[],
			WPVDB_PLAYGROUND_DEMO_VERSION,
			true
		);

		wp_localize_script(
			'wpvdb-playground-demo',
			'wpvdbDemo',
			[
				'restUrl'      => esc_url_raw( rest_url( 'wpvdb/v1/query' ) ),
				'nonce'        => wp_create_nonce( 'wp_rest' ),
				'presets'      => self::get_presets(),
				'postsByDocId' => self::get_posts_by_doc_id(),
				'limit'        => 5,
				'model'        => 'wpvdb-demo-' . ( defined( 'WPVDB_DEFAULT_EMBED_DIM' ) ? (int) WPVDB_DEFAULT_EMBED_DIM : 768 ),
				'i18n'         => [
					'tryPreset'    => __( 'Try one of these preset queries:', 'wpvdb-playground-demo' ),
					'results'      => __( 'Results', 'wpvdb-playground-demo' ),
					'document'     => __( 'Document', 'wpvdb-playground-demo' ),
					'distance'     => __( 'Distance', 'wpvdb-playground-demo' ),
					'preview'      => __( 'Preview', 'wpvdb-playground-demo' ),
					'noResults'    => __( 'No results.', 'wpvdb-playground-demo' ),
					'errorGeneric' => __( 'Query failed. Try again, or reload the page if the issue persists.', 'wpvdb-playground-demo' ),
					'errorNonce'   => __( 'Session expired. Reload the page to continue.', 'wpvdb-playground-demo' ),
				],
			]
		);
	}

	/**
	 * Render the demo preset widget into wpvdb's dashboard widget slot.
	 */
	public function render_preset_widget() {
		include WPVDB_PLAYGROUND_DEMO_DIR . 'views/dashboard-demo-panel.php';
	}
}
