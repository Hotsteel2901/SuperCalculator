import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_zh.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'generated/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('zh'),
  ];

  /// No description provided for @appTitle.
  ///
  /// In en, this message translates to:
  /// **'SuperCalculator - Next Era'**
  String get appTitle;

  /// No description provided for @home.
  ///
  /// In en, this message translates to:
  /// **'Home'**
  String get home;

  /// No description provided for @plotting.
  ///
  /// In en, this message translates to:
  /// **'Plotting'**
  String get plotting;

  /// No description provided for @calculus.
  ///
  /// In en, this message translates to:
  /// **'Calculus'**
  String get calculus;

  /// No description provided for @equations.
  ///
  /// In en, this message translates to:
  /// **'Equations'**
  String get equations;

  /// No description provided for @ode.
  ///
  /// In en, this message translates to:
  /// **'ODE'**
  String get ode;

  /// No description provided for @signals.
  ///
  /// In en, this message translates to:
  /// **'Signals'**
  String get signals;

  /// No description provided for @dataAnalysis.
  ///
  /// In en, this message translates to:
  /// **'Data'**
  String get dataAnalysis;

  /// No description provided for @statistics.
  ///
  /// In en, this message translates to:
  /// **'Statistics'**
  String get statistics;

  /// No description provided for @linearAlgebra.
  ///
  /// In en, this message translates to:
  /// **'Linear algebra'**
  String get linearAlgebra;

  /// No description provided for @tools.
  ///
  /// In en, this message translates to:
  /// **'Tools'**
  String get tools;

  /// No description provided for @settings.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get settings;

  /// No description provided for @about.
  ///
  /// In en, this message translates to:
  /// **'About'**
  String get about;

  /// No description provided for @welcomeTitle.
  ///
  /// In en, this message translates to:
  /// **'A clearer way to explore mathematics'**
  String get welcomeTitle;

  /// No description provided for @welcomeBody.
  ///
  /// In en, this message translates to:
  /// **'A Material 3 Expressive scientific calculator with a shared native computation core.'**
  String get welcomeBody;

  /// No description provided for @openPlotter.
  ///
  /// In en, this message translates to:
  /// **'Open plotter'**
  String get openPlotter;

  /// No description provided for @migrationStatus.
  ///
  /// In en, this message translates to:
  /// **'Flutter migration in progress'**
  String get migrationStatus;

  /// No description provided for @expression.
  ///
  /// In en, this message translates to:
  /// **'Expression'**
  String get expression;

  /// No description provided for @argumentX.
  ///
  /// In en, this message translates to:
  /// **'x value'**
  String get argumentX;

  /// No description provided for @evaluate.
  ///
  /// In en, this message translates to:
  /// **'Evaluate'**
  String get evaluate;

  /// No description provided for @clear.
  ///
  /// In en, this message translates to:
  /// **'Clear'**
  String get clear;

  /// No description provided for @quickExamples.
  ///
  /// In en, this message translates to:
  /// **'Quick examples'**
  String get quickExamples;

  /// No description provided for @result.
  ///
  /// In en, this message translates to:
  /// **'Result'**
  String get result;

  /// No description provided for @plotPreview.
  ///
  /// In en, this message translates to:
  /// **'Plot preview'**
  String get plotPreview;

  /// No description provided for @backend.
  ///
  /// In en, this message translates to:
  /// **'Backend'**
  String get backend;

  /// No description provided for @nativeFfi.
  ///
  /// In en, this message translates to:
  /// **'Native FFI'**
  String get nativeFfi;

  /// No description provided for @wasm.
  ///
  /// In en, this message translates to:
  /// **'WebAssembly'**
  String get wasm;

  /// No description provided for @dartFallback.
  ///
  /// In en, this message translates to:
  /// **'Dart fallback'**
  String get dartFallback;

  /// No description provided for @ready.
  ///
  /// In en, this message translates to:
  /// **'Ready'**
  String get ready;

  /// No description provided for @computing.
  ///
  /// In en, this message translates to:
  /// **'Computing…'**
  String get computing;

  /// No description provided for @invalidExpression.
  ///
  /// In en, this message translates to:
  /// **'Could not evaluate this expression.'**
  String get invalidExpression;

  /// No description provided for @noResult.
  ///
  /// In en, this message translates to:
  /// **'Enter an expression and evaluate it.'**
  String get noResult;

  /// No description provided for @featureComingSoon.
  ///
  /// In en, this message translates to:
  /// **'This feature is included in the migration matrix and is being connected incrementally.'**
  String get featureComingSoon;

  /// No description provided for @aboutBody.
  ///
  /// In en, this message translates to:
  /// **'SuperCalculator - Next Era replaces the legacy Tkinter and Java UI with one Flutter application while preserving the C computation core.'**
  String get aboutBody;

  /// The application version shown on the About page
  ///
  /// In en, this message translates to:
  /// **'Version {version}'**
  String versionLabel(Object version);

  /// No description provided for @version.
  ///
  /// In en, this message translates to:
  /// **'0.1.0'**
  String get version;

  /// Number of points currently rendered in the plot preview
  ///
  /// In en, this message translates to:
  /// **'{count} sampled points'**
  String plotPoints(Object count);

  /// Screen reader summary for the plot preview
  ///
  /// In en, this message translates to:
  /// **'Function plot for {expression}, with {count} finite samples.'**
  String accessibilityPlotSummary(Object count, Object expression);
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['en', 'zh'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppLocalizationsEn();
    case 'zh':
      return AppLocalizationsZh();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
